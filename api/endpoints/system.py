# api/endpoints/system.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import platform

router = APIRouter(prefix="/system", tags=["system"])

# Global dependencies
bot = None

def initialize_dependencies(bot_instance=None):
    global bot
    bot = bot_instance

@router.get("/health")
async def get_system_health():
    """Get comprehensive system health metrics"""
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = psutil.boot_time()
        
        # Network stats
        network = psutil.net_io_counters()
        
        # Process count
        process_count = len(psutil.pids())
        
        # System uptime
        uptime_seconds = datetime.now().timestamp() - boot_time
        
        # Bot-specific metrics
        guild = bot.guilds[0] if bot and bot.guilds else None
        bot_process = psutil.Process()
        bot_memory = bot_process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": round(cpu_percent, 1),
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "per_core": [round(usage, 1) for usage in psutil.cpu_percent(percpu=True, interval=0.1)]
            },
            "memory": {
                "usage_percent": round(memory.percent, 1),
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "cached_gb": round(getattr(memory, 'cached', 0) / (1024**3), 2),
                "buffers_gb": round(getattr(memory, 'buffers', 0) / (1024**3), 2)
            },
            "disk": {
                "usage_percent": round(disk.percent, 1),
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2)
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version(),
                "uptime_seconds": round(uptime_seconds),
                "process_count": process_count
            },
            "bot": {
                "memory_usage_mb": round(bot_memory, 2),
                "cpu_percent": round(bot_process.cpu_percent(), 2),
                "guild_count": len(bot.guilds) if bot else 0,
                "latency_ms": round(bot.latency * 1000, 1) if bot and bot.latency else 0,
                "connected_users": guild.member_count if guild else 0
            }
        }
    except Exception as e:
        return {"error": f"Failed to get system health: {str(e)}"}