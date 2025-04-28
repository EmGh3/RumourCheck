using System.Text.Json.Serialization;

namespace RumourCheck_front.ViewModels
{
    public class DailyStat
    {
        [JsonPropertyName("date")]
        public string Date { get; set; }

        [JsonPropertyName("count")]
        public int Count { get; set; }
    }
}