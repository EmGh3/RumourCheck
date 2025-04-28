namespace RumourCheck_front.Models
{
    public class DashboardStats
    {
        public int TotalAnalyses { get; set; }
        public int VerifiedNews { get; set; }  // Real news count
        public int FakeNewsDetected { get; set; }
    }
}
