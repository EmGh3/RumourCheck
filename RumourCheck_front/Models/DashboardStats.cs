using System.Text.Json.Serialization;

namespace RumourCheck_front.Models
{
    public class DashboardStats
    {
        [JsonPropertyName("total_analyses")]
        public int TotalAnalyses { get; set; }

        [JsonPropertyName("verified_news")]
        public int VerifiedNews { get; set; }

        [JsonPropertyName("fake_news_detected")]
        public int FakeNewsDetected { get; set; }
    }
}
