using RumourCheck_front.Models;

namespace RumourCheck_front.ViewModels
{
    public class DashboardViewModel
    {
        public int TotalAnalyses { get; set; }
        public int VerifiedNews { get; set; }
        public int FakeNewsDetected { get; set; }
        public List<RecentCheck> RecentChecks { get; set; } = new List<RecentCheck>();
        public List<DailyStat> DailyStats { get; set; }
        public string PieChartImage { get; set; }

        // Calculated properties
        public double AccuracyPercentage =>
            TotalAnalyses > 0 ? Math.Round((VerifiedNews + FakeNewsDetected) * 100.0 / TotalAnalyses, 1) : 0;

    }
    
}