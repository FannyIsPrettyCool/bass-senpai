#pragma once

#include <string>
#include <optional>
#include <filesystem>
#include <vector>

namespace bass_senpai {

class ArtworkHandler {
public:
    ArtworkHandler();
    explicit ArtworkHandler(const std::filesystem::path& cache_dir);
    
    std::optional<std::filesystem::path> get_artwork(const std::string& art_url);
    std::vector<std::string> render(const std::optional<std::string>& art_url, 
                                     int width, int height);
    
private:
    std::filesystem::path cache_dir_;
    std::string current_art_url_;
    std::optional<std::filesystem::path> current_cache_path_;
    bool is_kitty_;
    
    bool detect_kitty();
    std::filesystem::path get_cache_path(const std::string& art_url);
    std::optional<std::filesystem::path> download_artwork(const std::string& art_url);
    
    std::vector<std::string> render_textart(const std::filesystem::path& image_path, 
                                             int width, int height);
    std::vector<std::string> render_placeholder(int width, int height);
    
    // Image processing helpers
    struct RGB { uint8_t r, g, b; };
    std::vector<std::vector<RGB>> load_and_resize_image(
        const std::filesystem::path& path, int width, int height);
};

} // namespace bass_senpai
