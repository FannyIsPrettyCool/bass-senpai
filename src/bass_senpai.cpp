#include "bass_senpai.hpp"
#include <iostream>
#include <thread>
#include <chrono>
#include <csignal>

namespace bass_senpai {

BassSenpai* BassSenpai::instance_ = nullptr;

BassSenpai::BassSenpai(double update_interval)
    : update_interval_(update_interval)
    , mpris_(std::make_unique<MPRISClient>())
    , artwork_(std::make_unique<ArtworkHandler>())
    , ui_(std::make_unique<TerminalUI>())
    , running_(false)
{
    instance_ = this;
    
    // Set up signal handlers for graceful shutdown
    std::signal(SIGINT, [](int) { 
        if (instance_) instance_->stop(); 
    });
    std::signal(SIGTERM, [](int) { 
        if (instance_) instance_->stop(); 
    });
}

BassSenpai::~BassSenpai() {
    instance_ = nullptr;
}

void BassSenpai::stop() {
    running_ = false;
}

std::string BassSenpai::get_track_id(const std::optional<TrackMetadata>& metadata) {
    if (!metadata) {
        return "";
    }
    
    return metadata->artist + "|" + metadata->title + "|" + metadata->album;
}

int BassSenpai::run() {
    if (!mpris_->is_playerctl_available()) {
        std::cout << "Error: playerctl is not available.\n";
        std::cout << "Please install playerctl to use bass-senpai.\n\n";
        std::cout << "On Ubuntu/Debian: sudo apt install playerctl\n";
        std::cout << "On Arch Linux: sudo pacman -S playerctl\n";
        std::cout << "On macOS: brew install playerctl\n";
        return 1;
    }
    
    // Initialize terminal
    ui_->clear_screen();
    ui_->hide_cursor();
    
    running_ = true;
    
    try {
        while (running_) {
            update();
            std::this_thread::sleep_for(
                std::chrono::duration<double>(update_interval_));
        }
    } catch (...) {
        // Handle any exceptions
    }
    
    // Cleanup
    ui_->show_cursor();
    ui_->clear_screen();
    std::cout << "\nBass-senpai stopped.\n";
    
    return 0;
}

void BassSenpai::update() {
    // Update dimensions dynamically
    ui_->update_dimensions();
    
    // Get current metadata
    auto metadata = mpris_->get_metadata();
    
    // Determine if track changed
    std::string track_id = get_track_id(metadata);
    bool track_changed = track_id != last_track_id_;
    
    if (track_changed) {
        last_track_id_ = track_id;
    }
    
    // Get dynamic artwork dimensions
    int artwork_height = ui_->get_artwork_height();
    int artwork_width = ui_->get_artwork_width();
    
    // Render left panel (track info)
    auto left_panel = ui_->render_track_info(metadata, artwork_width + 2);
    
    // Render right panel (artwork)
    std::optional<std::string> art_url;
    if (metadata && !metadata->art_url.empty()) {
        art_url = metadata->art_url;
    }
    auto right_panel = artwork_->render(art_url, artwork_width, artwork_height);
    
    // Combine panels
    std::string combined = ui_->render_split_layout(left_panel, right_panel);
    
    // Display
    ui_->display(combined);
}

} // namespace bass_senpai
