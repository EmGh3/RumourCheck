using System;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using RumourCheck_front.Data;
using RumourCheck_front.Models;

namespace RumourCheck_front.Services
{
    public class UserAuthenticationService
    {
        private readonly ApplicationDbContext _context;

        public UserAuthenticationService(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<User?> RegisterAsync(RegisterViewModel model)
        {
            if (await _context.Users.AnyAsync(u => u.Email == model.Email))
                throw new InvalidOperationException("Email already registered");

            if (await _context.Users.AnyAsync(u => u.Username == model.Username))
                throw new InvalidOperationException("Username already taken");

            if (model.Password != model.ConfirmPassword)
                throw new InvalidOperationException("Passwords do not match");

            var user = new User
            {
                Username = model.Username,
                Email = model.Email,
                PasswordHash = HashPassword(model.Password),
                CreatedAt = DateTime.UtcNow,
                SearchHistories = new List<SearchHistory>()
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();
            return user;
        }

        public async Task<User?> LoginAsync(LoginViewModel model)
        {
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == model.Email);

            if (user == null || !VerifyPassword(model.Password, user.PasswordHash))
                return null;

            user.LastLogin = DateTime.UtcNow;
            await _context.SaveChangesAsync();
            return user;
        }

        public async Task AddSearchHistoryAsync(int userId, string query, string result)
        {
            var history = new SearchHistory
            {
                UserId = userId,
                SearchQuery = query,
                ResultSummary = result,
                Timestamp = DateTime.UtcNow,
                User = await _context.Users.FindAsync(userId)
            };

            _context.SearchHistories.Add(history);
            await _context.SaveChangesAsync();
        }

        private string HashPassword(string password)
        {
            using var sha256 = SHA256.Create();
            var bytes = Encoding.UTF8.GetBytes(password);
            var hash = sha256.ComputeHash(bytes);
            return Convert.ToBase64String(hash);
        }

        private bool VerifyPassword(string password, string hash)
        {
            var inputHash = HashPassword(password);
            return inputHash == hash;
        }
    }
}