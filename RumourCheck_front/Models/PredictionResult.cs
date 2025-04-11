namespace RumourCheck_front.Models
{
    public class PredictionResult
    {
        public bool prediction { get; set; }
        public double confidence_fake { get; set; }
        public double confidence_true { get; set; }
    }
}
