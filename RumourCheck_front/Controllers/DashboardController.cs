using Microsoft.AspNetCore.Mvc;

namespace RumourCheck_front.Controllers

{
    public class DashboardController : Controller
    {
        public IActionResult Index()
        {
            return View();
        }
    }
}