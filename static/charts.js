/**
 * STOCKSCOPE - TradingView Lightweight Charts Engine v2
 * Robust initialization and safety checks for financial data visualization.
 */

class StockChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.chart = null;
        this.series = null;
        this.volumeSeries = null;
        this.resizeObserver = null;
        
        if (this.container) {
            this.init();
        } else {
            console.error("Chart Container Not Found:", containerId);
        }
    }

    init() {
        try {
            if (typeof LightweightCharts === 'undefined') {
                console.error("TradingView Lightweight Charts Library Loading Error.");
                return;
            }

            // Ensure container has dimensions
            if (this.container.clientWidth === 0) {
                 this.container.style.minHeight = "600px";
            }

            const chartOptions = {
                layout: {
                    background: { type: 'solid', color: 'transparent' },
                    textColor: '#64748b',
                    fontSize: 10,
                    fontFamily: 'Inter',
                },
                grid: {
                    vertLines: { color: 'rgba(255, 255, 255, 0.02)' },
                    horzLines: { color: 'rgba(255, 255, 255, 0.02)' },
                },
                crosshair: {
                    mode: LightweightCharts.CrosshairMode.Normal,
                    vertLine: { color: '#1e293b', width: 1, style: 1 },
                    horzLine: { color: '#1e293b', width: 1, style: 1 },
                },
                rightPriceScale: {
                    borderColor: 'rgba(255, 255, 255, 0.05)',
                    autoScale: true,
                    scaleMargins: { top: 0.15, bottom: 0.25 },
                },
                timeScale: {
                    borderColor: 'rgba(255, 255, 255, 0.05)',
                    timeVisible: true,
                    secondsVisible: false,
                    fixLeftEdge: true,
                    fixRightEdge: true,
                },
                handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
                handleScale: { axisPressedMouseMove: true, mouseWheel: true, pinch: true },
            };

            this.chart = LightweightCharts.createChart(this.container, chartOptions);
            
            // Standard Candlestick implementation
            this.series = this.chart.addCandlestickSeries({
                upColor: '#10b981',
                downColor: '#f43f5e',
                borderUpColor: '#10b981',
                borderDownColor: '#f43f5e',
                wickUpColor: '#10b981',
                wickDownColor: '#f43f5e',
            });

            // Volume Overlay implementation
            this.volumeSeries = this.chart.addHistogramSeries({
                color: '#1e293b',
                priceFormat: { type: 'volume' },
                priceScaleId: '', // Overlay mode
            });

            this.volumeSeries.priceScale().applyOptions({
                scaleMargins: { top: 0.8, bottom: 0 },
            });

            // Responsive Logic
            this.resizeObserver = new ResizeObserver(entries => {
                if (entries.length === 0 || entries[0].target !== this.container) return;
                const newRect = entries[0].contentRect;
                if (this.chart) {
                    this.chart.applyOptions({ height: newRect.height, width: newRect.width });
                }
            });
            this.resizeObserver.observe(this.container);

        } catch (error) {
            console.error("Critical Chart Initialization Failure:", error);
        }
    }

    setData(ohlcData) {
        if (!this.series || !this.volumeSeries || !ohlcData || ohlcData.length === 0) return;
        
        try {
            // Sort by time (ascending) to satisfy Lightweight Charts data requirements
            ohlcData.sort((a, b) => {
                if (typeof a.time === 'number') return a.time - b.time;
                return a.time.localeCompare(b.time);
            });

            const candlestickData = ohlcData.map(d => ({
                time: d.time,
                open: parseFloat(d.open),
                high: parseFloat(d.high),
                low: parseFloat(d.low),
                close: parseFloat(d.close),
            }));

            const volumeData = ohlcData.map(d => ({
                time: d.time,
                value: parseFloat(d.volume),
                color: d.close >= d.open ? 'rgba(16, 185, 129, 0.2)' : 'rgba(244, 63, 94, 0.2)',
            }));

            this.series.setData(candlestickData);
            this.volumeSeries.setData(volumeData);
            this.chart.timeScale().fitContent();
        } catch (e) {
            console.error("Data Transformation Failure:", e);
        }
    }

    async updateRange(ticker, period, interval) {
        try {
            const response = await fetch(`/api/stock_data?ticker=${ticker}&period=${period}&interval=${interval}`);
            const data = await response.json();
            if (data.success && data.ohlc) {
                this.setData(data.ohlc);
                return true;
            }
            return false;
        } catch (error) {
            console.error("Async Range Update Failed:", error);
            return false;
        }
    }
}

// Global initialization entry point
window.initStockChart = (containerId, initialData) => {
    try {
        const instance = new StockChart(containerId);
        if (initialData && instance.series) {
            instance.setData(initialData);
        }
        return instance;
    } catch (e) {
        console.error("Top-level initStockChart error:", e);
        return null;
    }
};
