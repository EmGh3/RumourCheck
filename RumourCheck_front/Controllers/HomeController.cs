using Microsoft.AspNetCore.Mvc;
using RumourCheck_front.Models;
using System.Diagnostics;
using System.Text.Json;
using System.Text;
using RumourCheck_front.ViewModels;

public class HomeController : Controller
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<HomeController> _logger;

    public HomeController(
        IHttpClientFactory httpClientFactory, 
        ILogger<HomeController> logger)
    {
        _httpClient = httpClientFactory.CreateClient();
        _httpClient.BaseAddress = new Uri("http://localhost:8000");
        _logger = logger;
    }

    public IActionResult Index()
    {
        return View();
    }
    public IActionResult About()
    {
        return View();
    }
    public IActionResult Privacy()
    {
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> CheckNews(string text)
    {
            // Create request object matching FastAPI model
            var request = new
            {
                text = text
            };

            // Serialize
            var jsonString = JsonSerializer.Serialize(request);

            // Create HTTP content
            var content = new StringContent(
                jsonString,
                Encoding.UTF8,
                "application/json");

            // Send request
            var response = await _httpClient.PostAsync("/predict", content);
            var responseContent = await response.Content.ReadAsStringAsync();
            _logger.LogInformation($"API Response: {responseContent}");

            if (!response.IsSuccessStatusCode)
            {
                return BadRequest($"API Error: {response.StatusCode} - {responseContent}");
            }

            // Deserialize
            var result = JsonSerializer.Deserialize<PredictionResult>(responseContent);

            return View("Results", new PredictionResultViewModel
            {
                Text = text,
                Prediction = result.prediction,
                FakeConfidence = result.confidence_fake,
                TrueConfidence = result.confidence_true
            });
        }
    
}

