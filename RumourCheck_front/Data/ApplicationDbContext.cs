using Microsoft.EntityFrameworkCore;
using RumourCheck_front.Models;

namespace RumourCheck_front.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
        public DbSet<SearchHistory> SearchHistories { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure User entity
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Username).IsRequired().HasMaxLength(50);
                entity.Property(e => e.Email).IsRequired().HasMaxLength(100);
                entity.Property(e => e.PasswordHash).IsRequired().HasMaxLength(255);
                entity.HasIndex(e => e.Email).IsUnique();
                entity.HasIndex(e => e.Username).IsUnique();
            });

            // Configure SearchHistory entity
            modelBuilder.Entity<SearchHistory>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.SearchQuery).IsRequired();
                entity.Property(e => e.IsFake).IsRequired(); // Added
                entity.Property(e => e.FakeConfidence).IsRequired(); // Added
                entity.Property(e => e.TrueConfidence).IsRequired(); // Added
                entity.Property(e => e.Timestamp).IsRequired(); // Added for consistency
                entity.HasOne(d => d.User)
                    .WithMany(p => p.SearchHistories)
                    .HasForeignKey(d => d.UserId)
                    .OnDelete(DeleteBehavior.Cascade);
            });
        }
    }
}
