using Microsoft.AspNetCore.Mvc;
using RumourCheck_front.Data;
using RumourCheck_front.Models;
using RumourCheck_front.ViewModels;
using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;

public class DashboardController : Controller
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<DashboardController> _logger;
    private readonly HttpClient _httpClient;

    public DashboardController(ApplicationDbContext context, ILogger<DashboardController> logger, IHttpClientFactory httpClientFactory)
    {
        _context = context;
        _logger = logger;
        _httpClient = httpClientFactory.CreateClient();
        _httpClient.BaseAddress = new Uri("http://localhost:8000");
    }

    public async Task<IActionResult> Index()
    {
        var viewModel = new DashboardViewModel();
        string userIdStr = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
        {
            _logger.LogError("User is not authenticated or invalid user ID");
            return View("Error", new ErrorViewModel { });
        }

        try
        {
            var userSearches = await _context.SearchHistories
                .Where(h => h.UserId == userId)
                .OrderByDescending(h => h.Timestamp)
                .ToListAsync();

            viewModel.TotalAnalyses = userSearches.Count();
            viewModel.FakeNewsDetected = userSearches.Count(h => !h.IsFake); // Swapped
            viewModel.VerifiedNews = userSearches.Count(h => h.IsFake); // Swapped

            viewModel.RecentChecks = userSearches.Take(5).Select(h => new RecentCheck
            {
                Text = h.SearchQuery.Length > 100 ? h.SearchQuery.Substring(0, 100) + "..." : h.SearchQuery,
                IsFake = h.IsFake,
                Date = h.Timestamp.ToString("dd/MM/yyyy")
            }).ToList();

            viewModel.DailyStats = userSearches
                .GroupBy(h => h.Timestamp.Date)
                .Select(g => new DailyStat
                {
                    Date = g.Key.ToString("yyyy-MM-dd"),
                    Count = g.Count()
                })
                .OrderByDescending(d => d.Date)
                .Take(7)
                .ToList();

            var pieResponse = await _httpClient.GetAsync($"/analytics/truth-pie-chart/{userId}");
            if (pieResponse.IsSuccessStatusCode)
            {
                var imageBytes = await pieResponse.Content.ReadAsByteArrayAsync();
                if (imageBytes.Length > 0)
                {
                    viewModel.PieChartImage = Convert.ToBase64String(imageBytes);
                    _logger.LogInformation($"Pie chart fetched successfully for user {userId}, image size: {imageBytes.Length} bytes");
                }
                else
                {
                    _logger.LogWarning($"Empty pie chart image received for user {userId}");
                    viewModel.PieChartImage = "";
                }
            }
            else
            {
                var errorContent = await pieResponse.Content.ReadAsStringAsync();
                _logger.LogWarning($"Failed to fetch pie chart for user {userId}: {pieResponse.StatusCode} - {errorContent}");
                viewModel.PieChartImage = "";
            }

            return View(viewModel);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading dashboard data");
            return View("Error", new ErrorViewModel { });
        }
    }
}