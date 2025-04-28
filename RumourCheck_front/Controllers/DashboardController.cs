// DashboardController.cs
using Microsoft.AspNetCore.Mvc;
using RumourCheck_front.Models;
using System.Diagnostics;
using System.Text.Json;
using System.Text;
using RumourCheck_front.ViewModels;
using Microsoft.AspNetCore.Http.Json;

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
        var viewModel = new DashboardViewModel();

        try
        {
            // Get basic stats
            var statsResponse = await _httpClient.GetAsync("/dashboard/stats");
            if (statsResponse.IsSuccessStatusCode)
            {
                var stats = await statsResponse.Content.ReadFromJsonAsync<DashboardStats>();
                viewModel.TotalAnalyses = stats?.TotalAnalyses ?? 0;
                viewModel.VerifiedNews = stats?.VerifiedNews ?? 0;
                viewModel.FakeNewsDetected = stats?.FakeNewsDetected ?? 0;
            }

            // Get recent checks
            var checksResponse = await _httpClient.GetAsync("/dashboard/recent-checks");
            if (checksResponse.IsSuccessStatusCode)
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                };
                viewModel.RecentChecks = await checksResponse.Content
                    .ReadFromJsonAsync<List<RecentCheck>>(options) ?? new List<RecentCheck>();
            }

            // Get daily stats
            var dailyResponse = await _httpClient.GetAsync("/analytics/daily-stats");
            if (dailyResponse.IsSuccessStatusCode)
            {
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                };
                viewModel.DailyStats = await dailyResponse.Content
                    .ReadFromJsonAsync<List<DailyStat>>(options) ?? new List<DailyStat>();
            }

            // Get pie chart
            var pieResponse = await _httpClient.GetAsync("/analytics/truth-pie-chart");
            if (pieResponse.IsSuccessStatusCode)
            {
                var pieData = await pieResponse.Content.ReadFromJsonAsync<Dictionary<string, string>>();
                viewModel.PieChartImage = pieData?["image"] ?? string.Empty;
            }

            return View(viewModel);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading dashboard data");
            return View("Error", new ErrorViewModel {});
        }
    }
}