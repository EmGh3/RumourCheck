using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using RumourCheck_front.Data;
using RumourCheck_front.Models;

namespace RumourCheck_front.Services
{
    public class SearchHistoryService
    {
        private readonly ApplicationDbContext _context;

        public SearchHistoryService(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task AddSearchHistoryAsync(string searchQuery, string resultSummary, int userId)
        {
            var history = new SearchHistory
            {
                SearchQuery = searchQuery,
                ResultSummary = resultSummary,
                UserId = userId,
                Timestamp = DateTime.Now,
                User = await _context.Users.FindAsync(userId)
            };

            await _context.SearchHistories.AddAsync(history);
            await _context.SaveChangesAsync();
        }

        public async Task<int> GetCurrentUserIdAsync(ClaimsPrincipal user)
        {
            if (user == null)
            {
                throw new InvalidOperationException("User is not authenticated");
            }

            return int.Parse(user.FindFirst(ClaimTypes.NameIdentifier).Value);
        }
    }
}
