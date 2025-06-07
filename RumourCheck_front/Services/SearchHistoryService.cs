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

        public async Task AddSearchHistoryAsync(string searchQuery, bool isFake, double fakeConfidence, double trueConfidence, int userId)
        {
            var user = await _context.Users.FindAsync(userId);
            if (user == null)
            {
                throw new InvalidOperationException($"User with ID {userId} not found");
            }

            var history = new SearchHistory
            {
                SearchQuery = searchQuery,
                IsFake = isFake,
                FakeConfidence = fakeConfidence,
                TrueConfidence = trueConfidence,
                UserId = userId,
                Timestamp = DateTime.Now,
                User = user
            };
            await _context.SearchHistories.AddAsync(history);
            await _context.SaveChangesAsync();
        }

        public int GetCurrentUserId(ClaimsPrincipal user)
        {
            if (user == null || !user.Identity.IsAuthenticated)
            {
                throw new InvalidOperationException("User is not authenticated");
            }

            var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier);
            if (userIdClaim == null)
            {
                throw new InvalidOperationException("User ID claim not found");
            }

            if (!int.TryParse(userIdClaim.Value, out int userId))
            {
                throw new InvalidOperationException("Invalid user ID format");
            }

            return userId;
        }
    }
}