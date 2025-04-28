// DashboardController.cs
using Microsoft.AspNetCore.Mvc;
using RumourCheck_front.Models;
using System.Diagnostics;
using System.Text.Json;
using System.Text;
using RumourCheck_front.ViewModels;

public class DashboardController : Controller
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<DashboardController> _logger;
    private readonly IConfiguration _configuration;

    public DashboardController(
        IHttpClientFactory httpClientFactory,
        ILogger<DashboardController> logger,
        IConfiguration configuration)
    {
        _httpClient = httpClientFactory.CreateClient();
        _httpClient.BaseAddress = new Uri(configuration["BackendApi:BaseUrl"]);
        _logger = logger;
        _configuration = configuration;
    }

    public async Task<IActionResult> Index()
    {
        try
        {
            // Get dashboard statistics
            var statsResponse = await _httpClient.GetAsync("/Dashboard/stats");
            statsResponse.EnsureSuccessStatusCode();
            var stats = await statsResponse.Content.ReadFromJsonAsync<DashboardStats>();

            // Get recent checks
            var checksResponse = await _httpClient.GetAsync("/Dashboard/recent-checks");
            checksResponse.EnsureSuccessStatusCode();
            var recentChecks = await checksResponse.Content.ReadFromJsonAsync<List<RecentCheck>>();

            return View(new DashboardViewModel
            {
                TotalAnalyses = stats?.TotalAnalyses ?? 0,
                VerifiedNews = stats?.VerifiedNews ?? 0,
                FakeNewsDetected = stats?.FakeNewsDetected ?? 0,
                RecentChecks = recentChecks ?? new List<RecentCheck>()
            });
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Error fetching dashboard data from API");

            // Fallback data when API is unavailable
            return View(new DashboardViewModel
            {
                TotalAnalyses = 12,
                VerifiedNews = 8,
                FakeNewsDetected = 4,
                RecentChecks = new List<RecentCheck>
                {
                    new RecentCheck
                    {
                        Text = "Le changement climatique est confirmé par 97% des scientifiques",
                        IsFake = false,
                        Date = DateTime.Now.AddDays(-2)
                    },
                    new RecentCheck
                    {
                        Text = "Nouvelle taxe annoncée pour les véhicules électriques - FAKE",
                        IsFake = true,
                        Date = DateTime.Now.AddDays(-1)
                    }
                }
            });
        }
    }
}