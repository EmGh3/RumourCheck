using System.Security.Claims;

using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using RumourCheck_front.Data;
using RumourCheck_front.Models;

namespace RumourCheck_front.Controllers
{
    [Authorize]
    public class SearchHistoryController : Controller
    {
        private readonly ApplicationDbContext _context;

        public SearchHistoryController(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<IActionResult> Index()
        {
            var userId = int.Parse(User.FindFirst(ClaimTypes.NameIdentifier).Value);
            var history = await _context.SearchHistories
                .Where(h => h.UserId == userId)
                .OrderByDescending(h => h.Timestamp)
                .ToListAsync();

            return View(history);
        }

        [HttpPost]
        public async Task<IActionResult> Delete(int id)
        {
            var userId = int.Parse(User.FindFirst(ClaimTypes.NameIdentifier).Value);
            var history = await _context.SearchHistories
                .FirstOrDefaultAsync(h => h.Id == id && h.UserId == userId);

            if (history != null)
            {
                _context.SearchHistories.Remove(history);
                await _context.SaveChangesAsync();
            }

            return RedirectToAction(nameof(Index));
        }
    }
}
