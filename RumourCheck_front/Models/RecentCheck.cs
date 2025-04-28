using System.Text.Json.Serialization;

namespace RumourCheck_front.Models
{
    public class RecentCheck
    {
        [JsonPropertyName("text")]
        public string Text { get; set; }

        [JsonPropertyName("is_fake")]
        public bool IsFake { get; set; }

        [JsonPropertyName("date")]
        public DateTime Date { get; set; }
    }
}
