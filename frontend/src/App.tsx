import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Header } from './components/Header';
import { VideoPlayer } from './components/VideoPlayer';
import { TelemetryCards } from './components/TelemetryCards';
import { ControlSidebar, AppConfig } from './components/ControlSidebar';
import { PolicyModal } from './components/PolicyModal';

const API_BASE = 'http://127.0.0.1:8000';

export const App: React.FC = () => {
  // Config state
  const [config, setConfig] = useState<AppConfig>({
    confidence_threshold: 0.25,
    model_id: 'yolov8m-640',
    trigger_anchor: 'BOTTOM_CENTER',
    zone_offset_x: 0,
    zone_offset_y: 0,
    zone_scale: 1.0,
    hourly_rate: 5.0,
    total_capacity: 7,
    operating_hours_per_day: 12.5,
  });

  // Telemetry state
  const [telemetry, setTelemetry] = useState({
    occupancy_percentage: 0.0,
    smoothed_occupied_count: 0,
    raw_occupied_count: 0,
    total_detected_count: 0,
    hourly_opportunity_cost: 0.0,
    daily_opportunity_cost: 0.0,
    annual_opportunity_cost: 0.0,
    last_updated: 0.0,
  });

  const [isConnected, setIsConnected] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isPolicyOpen, setIsPolicyOpen] = useState(false);

  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Sync config changes to backend
  const pushConfigToBackend = useCallback((updated: Partial<AppConfig>) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(async () => {
      try {
        await fetch(`${API_BASE}/api/v1/config`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updated),
        });
      } catch (err) {
        console.error('Failed to sync config:', err);
      }
    }, 200);
  }, []);

  const handleConfigChange = (newConfig: Partial<AppConfig>) => {
    setConfig((prev) => {
      const merged = { ...prev, ...newConfig };
      pushConfigToBackend(newConfig);
      return merged;
    });
  };

  const handleResetZone = async () => {
    try {
      await fetch(`${API_BASE}/api/v1/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reset_zone: true }),
      });
      setConfig((prev) => ({
        ...prev,
        zone_offset_x: 0,
        zone_offset_y: 0,
        zone_scale: 1.0,
      }));
    } catch (err) {
      console.error('Failed to reset zone:', err);
    }
  };

  // Force Snapshot Refresh
  const handleForceRefresh = async () => {
    setIsRefreshing(true);
    try {
      await fetch(`${API_BASE}/api/v1/refresh`, { method: 'POST' });
    } catch (err) {
      console.error('Failed to force refresh:', err);
    } finally {
      setTimeout(() => setIsRefreshing(false), 600);
    }
  };

  // Poll analytics telemetry
  useEffect(() => {
    let isMounted = true;

    const fetchTelemetry = async () => {
      try {
        const query = new URLSearchParams({
          hourly_rate: config.hourly_rate.toString(),
          total_capacity: config.total_capacity.toString(),
          operating_hours_per_day: config.operating_hours_per_day.toString(),
        });
        const res = await fetch(`${API_BASE}/api/v1/analytics?${query.toString()}`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setTelemetry({
              occupancy_percentage: data.occupancy_percentage || 0.0,
              smoothed_occupied_count: data.smoothed_occupied_count || 0,
              raw_occupied_count: data.raw_occupied_count || 0,
              total_detected_count: data.total_detected_count || 0,
              hourly_opportunity_cost: data.hourly_opportunity_cost || 0.0,
              daily_opportunity_cost: data.daily_opportunity_cost || 0.0,
              annual_opportunity_cost: data.annual_opportunity_cost || 0.0,
              last_updated: data.last_updated || Date.now(),
            });
            setIsConnected(true);
          }
        } else {
          if (isMounted) setIsConnected(false);
        }
      } catch {
        if (isMounted) setIsConnected(false);
      }
    };

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 1000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [config.hourly_rate, config.total_capacity, config.operating_hours_per_day]);

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 flex flex-col selection:bg-emerald-500/20">
      {/* Top Navigation Header */}
      <Header
        isConnected={isConnected}
        isRefreshing={isRefreshing}
        onRefresh={handleForceRefresh}
        onOpenPolicy={() => setIsPolicyOpen(true)}
      />

      {/* Main Dashboard Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        <div className="flex flex-col lg:flex-row gap-6 items-start">
          {/* Main Visual & Telemetry Section (Left / Center) */}
          <div className="flex-1 w-full space-y-6">
            {/* Live MJPEG Feed Player */}
            <VideoPlayer
              streamUrl={`${API_BASE}/api/v1/stream`}
              modelId={config.model_id}
              confidence={config.confidence_threshold}
              occupiedCount={telemetry.smoothed_occupied_count}
              totalCapacity={config.total_capacity}
              totalDetected={telemetry.total_detected_count}
            />

            {/* Financial Opportunity Cost Cards */}
            <TelemetryCards
              occupancyPercentage={telemetry.occupancy_percentage}
              smoothedOccupiedCount={telemetry.smoothed_occupied_count}
              totalCapacity={config.total_capacity}
              hourlyCost={telemetry.hourly_opportunity_cost}
              dailyCost={telemetry.daily_opportunity_cost}
              annualCost={telemetry.annual_opportunity_cost}
              hourlyRate={config.hourly_rate}
              operatingHours={config.operating_hours_per_day}
            />
          </div>

          {/* Interactive Tuning & Calibration Controls (Right / Sidebar) */}
          <ControlSidebar
            config={config}
            onConfigChange={handleConfigChange}
            onResetZone={handleResetZone}
          />
        </div>
      </main>

      {/* Policy Context Modal */}
      <PolicyModal isOpen={isPolicyOpen} onClose={() => setIsPolicyOpen(false)} />
    </div>
  );
};

export default App;
