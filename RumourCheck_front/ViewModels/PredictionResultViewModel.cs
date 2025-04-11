namespace RumourCheck_front.ViewModels
{

    public class PredictionResultViewModel
    {
        public string Text { get; set; }
        public bool Prediction { get; set; }
        public double FakeConfidence { get; set; }
        public double TrueConfidence { get; set; }
    }
}
