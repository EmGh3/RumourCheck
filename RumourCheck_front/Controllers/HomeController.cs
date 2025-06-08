using Microsoft.AspNetCore.Mvc;
using RumourCheck_front.Models;
using System.Text.Json;
using System.Text;
using RumourCheck_front.ViewModels;
using RumourCheck_front.Services;
using System.Security.Claims;

public class HomeController : Controller
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<HomeController> _logger;
    private readonly SearchHistoryService _searchHistoryService;

    public HomeController(
        IHttpClientFactory httpClientFactory,
        ILogger<HomeController> logger,
        SearchHistoryService searchHistoryService)
    {
        _httpClient = httpClientFactory.CreateClient();
        _httpClient.BaseAddress = new Uri("http://localhost:8000");
        _logger = logger;
        _searchHistoryService = searchHistoryService;
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
        try
        {
            var userId = _searchHistoryService.GetCurrentUserId(User);
            _logger.LogInformation($"Sending user_id: {userId} with text: {text}");
            var request = new { text = text, user_id = userId };
            var jsonString = JsonSerializer.Serialize(request);
            _logger.LogInformation($"Request JSON: {jsonString}");
            var content = new StringContent(jsonString, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("/predict", content);
            var responseContent = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError($"API Error: {response.StatusCode} - {responseContent}");
                return BadRequest($"API Error: {response.StatusCode} - {responseContent}");
            }

            var result = JsonSerializer.Deserialize<PredictionResult>(responseContent);

            // Invert IsFake logic: prediction=True (fake) -> IsFake=false (true news)
            await _searchHistoryService.AddSearchHistoryAsync(
                text,
                result.prediction, // Invert prediction
                result.confidence_fake,
                result.confidence_true,
                userId
            );

            return View("Results", new PredictionResultViewModel
            {
                Text = text,
                Prediction = result.prediction, 
                FakeConfidence = result.confidence_fake,
                TrueConfidence = result.confidence_true
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing news check");
            return View("Error", new ErrorViewModel { });
        }
    }
}