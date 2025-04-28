namespace RumourCheck_front.ViewModels
{

    public class PredictionResultViewModel
    {
        public string Text { get; set; }
        public bool Prediction { get; set; }
        public double FakeConfidence { get; set; }
        public double TrueConfidence { get; set; }
        public DateTime verifiedAt { get; set; }
        // Formatted properties for view
        public string FormattedPrediction => Prediction ? "Fake News" : "Verified News";
        public string PredictionClass => Prediction ? "fake" : "true";
        public int FakePercentage => (int)(FakeConfidence * 100);
        public int TruePercentage => (int)(TrueConfidence * 100);
    }

}

