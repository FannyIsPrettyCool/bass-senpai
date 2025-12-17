#include "artwork_handler.hpp"
#include <curl/curl.h>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <cstdlib>
#include <algorithm>

// STB image implementation
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_RESIZE_IMPLEMENTATION
#include "stb_image.h"
#include "stb_image_resize2.h"

namespace bass_senpai {

// Helper for MD5 hashing (simple implementation for cache keys)
static std::string md5_hash(const std::string& input) {
    // For simplicity, we'll use a simple hash function
    // In production, you'd want to use a proper MD5 library
    std::hash<std::string> hasher;
    size_t hash = hasher(input);
    
    std::stringstream ss;
    ss << std::hex << std::setfill('0') << std::setw(16) << hash;
    return ss.str();
}

// CURL write callback
static size_t write_callback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

ArtworkHandler::ArtworkHandler() 
    : ArtworkHandler(std::filesystem::path(std::getenv("HOME")) / ".cache" / "bass-senpai" / "artwork") 
{}

ArtworkHandler::ArtworkHandler(const std::filesystem::path& cache_dir)
    : cache_dir_(cache_dir)
    , is_kitty_(detect_kitty()) 
{
    std::filesystem::create_directories(cache_dir_);
}

bool ArtworkHandler::detect_kitty() {
    const char* term = std::getenv("TERM");
    if (term) {
        std::string term_str(term);
        std::transform(term_str.begin(), term_str.end(), term_str.begin(), ::tolower);
        return term_str.find("kitty") != std::string::npos;
    }
    return false;
}

std::filesystem::path ArtworkHandler::get_cache_path(const std::string& art_url) {
    std::string hash = md5_hash(art_url);
    return cache_dir_ / (hash + ".jpg");
}

std::optional<std::filesystem::path> ArtworkHandler::download_artwork(const std::string& art_url) {
    try {
        auto cache_path = get_cache_path(art_url);
        
        // Handle file:// URLs
        if (art_url.substr(0, 7) == "file://") {
            std::string local_path = art_url.substr(7);
            
            // Load image and save to cache
            int width, height, channels;
            unsigned char* data = stbi_load(local_path.c_str(), &width, &height, &channels, 3);
            if (!data) {
                return std::nullopt;
            }
            
            // Save as JPEG
            // Note: You'd need stb_image_write.h for this, or just copy the file
            std::filesystem::copy_file(local_path, cache_path, 
                                      std::filesystem::copy_options::overwrite_existing);
            stbi_image_free(data);
            
            return cache_path;
        }
        
        // Download from HTTP(S)
        CURL* curl = curl_easy_init();
        if (!curl) {
            return std::nullopt;
        }
        
        std::string response_data;
        
        curl_easy_setopt(curl, CURLOPT_URL, art_url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 5L);
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
        
        CURLcode res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);
        
        if (res != CURLE_OK || response_data.empty()) {
            return std::nullopt;
        }
        
        // Save to cache
        std::ofstream out(cache_path, std::ios::binary);
        out.write(response_data.data(), response_data.size());
        out.close();
        
        return cache_path;
    } catch (...) {
        return std::nullopt;
    }
}

std::optional<std::filesystem::path> ArtworkHandler::get_artwork(const std::string& art_url) {
    if (art_url.empty()) {
        current_art_url_.clear();
        current_cache_path_ = std::nullopt;
        return std::nullopt;
    }
    
    // Check if this is the same artwork as before
    if (art_url == current_art_url_ && current_cache_path_ && 
        std::filesystem::exists(*current_cache_path_)) {
        return current_cache_path_;
    }
    
    // Update current URL
    current_art_url_ = art_url;
    
    // Check cache first
    auto cache_path = get_cache_path(art_url);
    if (std::filesystem::exists(cache_path)) {
        current_cache_path_ = cache_path;
        return cache_path;
    }
    
    // Download and cache
    auto downloaded = download_artwork(art_url);
    current_cache_path_ = downloaded;
    return downloaded;
}

std::vector<std::vector<ArtworkHandler::RGB>> ArtworkHandler::load_and_resize_image(
    const std::filesystem::path& path, int width, int height) 
{
    int orig_width, orig_height, channels;
    unsigned char* data = stbi_load(path.string().c_str(), &orig_width, &orig_height, &channels, 3);
    
    if (!data) {
        return {};
    }
    
    // Resize image
    std::vector<unsigned char> resized(width * height * 3);
    stbir_resize_uint8_linear(data, orig_width, orig_height, 0,
                               resized.data(), width, height, 0, STBIR_RGB);
    
    stbi_image_free(data);
    
    // Convert to RGB vector
    std::vector<std::vector<RGB>> result(height, std::vector<RGB>(width));
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int idx = (y * width + x) * 3;
            result[y][x] = {resized[idx], resized[idx + 1], resized[idx + 2]};
        }
    }
    
    return result;
}

std::vector<std::string> ArtworkHandler::render_textart(
    const std::filesystem::path& image_path, int width, int height) 
{
    auto pixels = load_and_resize_image(image_path, width, height * 2);
    
    if (pixels.empty()) {
        return render_placeholder(width, height);
    }
    
    std::vector<std::string> output;
    
    // Top border
    std::string top_border = "╔";
    for (int i = 0; i < width; ++i) top_border += "═";
    top_border += "╗";
    output.push_back(top_border);
    
    // Use half-block characters for better resolution
    for (int y = 0; y < height * 2; y += 2) {
        std::string line = "║";
        for (int x = 0; x < width; ++x) {
            auto& upper = pixels[y][x];
            auto& lower = (y + 1 < height * 2) ? pixels[y + 1][x] : pixels[y][x];
            
            // Use upper half block (▀) with appropriate colors
            std::stringstream ss;
            ss << "\x1b[38;2;" << (int)upper.r << ";" << (int)upper.g << ";" << (int)upper.b << "m"
               << "\x1b[48;2;" << (int)lower.r << ";" << (int)lower.g << ";" << (int)lower.b << "m▀\x1b[0m";
            line += ss.str();
        }
        line += "║";
        output.push_back(line);
    }
    
    // Bottom border
    std::string bottom_border = "╚";
    for (int i = 0; i < width; ++i) bottom_border += "═";
    bottom_border += "╝";
    output.push_back(bottom_border);
    
    return output;
}

std::vector<std::string> ArtworkHandler::render_placeholder(int width, int height) {
    std::vector<std::string> lines;
    
    // Top border
    std::string top_border = "╔";
    for (int i = 0; i < width; ++i) top_border += "═";
    top_border += "╗";
    lines.push_back(top_border);
    
    // Middle lines with vertical borders
    for (int y = 0; y < height; ++y) {
        if (y == height / 2) {
            std::string text = "No Artwork";
            int padding = (width - text.length()) / 2;
            std::string content(padding, ' ');
            content += text;
            content += std::string(width - padding - text.length(), ' ');
            lines.push_back("║" + content + "║");
        } else {
            lines.push_back("║" + std::string(width, ' ') + "║");
        }
    }
    
    // Bottom border
    std::string bottom_border = "╚";
    for (int i = 0; i < width; ++i) bottom_border += "═";
    bottom_border += "╝";
    lines.push_back(bottom_border);
    
    return lines;
}

std::vector<std::string> ArtworkHandler::render(
    const std::optional<std::string>& art_url, int width, int height) 
{
    if (!art_url) {
        return render_placeholder(width, height);
    }
    
    auto artwork_path = get_artwork(*art_url);
    
    if (!artwork_path || !std::filesystem::exists(*artwork_path)) {
        return render_placeholder(width, height);
    }
    
    // For now, just use text art (Kitty protocol would need more work)
    return render_textart(*artwork_path, width, height);
}

} // namespace bass_senpai
