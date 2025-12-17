#pragma once

#include "mpris_client.hpp"
#include <string>
#include <vector>
#include <optional>

namespace bass_senpai {

class TerminalUI {
public:
    TerminalUI();
    
    void clear_screen();
    void hide_cursor();
    void show_cursor();
    void display(const std::string& content);
    
    int get_artwork_width() const { return artwork_width_; }
    int get_artwork_height() const { return artwork_height_; }
    
    void update_dimensions();
    
    std::vector<std::string> render_track_info(
        const std::optional<TrackMetadata>& metadata, 
        int artwork_width);
    
    std::string render_split_layout(
        const std::vector<std::string>& left_panel,
        const std::vector<std::string>& right_panel);

private:
    int term_width_;
    int term_height_;
    int artwork_width_;
    int artwork_height_;
    std::string last_output_;
    
    int get_terminal_width();
    int get_terminal_height();
    void calculate_artwork_size();
    
    std::string format_time(double seconds);
    std::string create_progress_bar(double position, double length, int width);
    std::string get_status_icon(const std::string& status);
    std::string get_status_color(const std::string& status);
    std::string truncate(const std::string& text, int max_length);
    std::string strip_ansi(const std::string& text);
    int display_width(const std::string& text);
    
    std::vector<std::string> center_content_vertically(
        const std::vector<std::string>& content_lines);
    
    std::vector<std::string> render_no_player(int artwork_width);
    
    static constexpr int ARTWORK_BORDER_HEIGHT = 2;
};

} // namespace bass_senpai
