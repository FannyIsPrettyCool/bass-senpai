#include "terminal_ui.hpp"
#include <sys/ioctl.h>
#include <unistd.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <regex>
#include <algorithm>
#include <cwchar>
#include <clocale>

namespace bass_senpai {

TerminalUI::TerminalUI() 
    : term_width_(get_terminal_width())
    , term_height_(get_terminal_height())
{
    // Set locale for proper wide character handling
    std::setlocale(LC_ALL, "");
    calculate_artwork_size();
}

int TerminalUI::get_terminal_width() {
    struct winsize w;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &w) == 0) {
        return w.ws_col;
    }
    return 120;  // Default fallback
}

int TerminalUI::get_terminal_height() {
    struct winsize w;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &w) == 0) {
        return w.ws_row;
    }
    return 30;  // Default fallback
}

void TerminalUI::update_dimensions() {
    term_width_ = get_terminal_width();
    term_height_ = get_terminal_height();
    calculate_artwork_size();
}

void TerminalUI::calculate_artwork_size() {
    // Calculate artwork dimensions based on terminal size
    if (term_width_ < 80) {
        artwork_width_ = 20;
        artwork_height_ = 10;
    } else if (term_width_ < 120) {
        artwork_width_ = 30;
        artwork_height_ = 15;
    } else {
        artwork_width_ = 40;
        artwork_height_ = 20;
    }
}

void TerminalUI::clear_screen() {
    std::cout << "\x1b[2J\x1b[H" << std::flush;
}

void TerminalUI::hide_cursor() {
    std::cout << "\x1b[?25l" << std::flush;
}

void TerminalUI::show_cursor() {
    std::cout << "\x1b[?25h" << std::flush;
}

std::string TerminalUI::format_time(double seconds) {
    if (seconds < 0) seconds = 0;
    int minutes = static_cast<int>(seconds) / 60;
    int secs = static_cast<int>(seconds) % 60;
    
    std::stringstream ss;
    ss << std::setfill('0') << std::setw(2) << minutes << ":"
       << std::setfill('0') << std::setw(2) << secs;
    return ss.str();
}

std::string TerminalUI::create_progress_bar(double position, double length, int width) {
    double percentage = (length <= 0) ? 0.0 : std::min(1.0, position / length);
    int filled = static_cast<int>(percentage * width);
    int empty = width - filled;
    
    // Stylized progress bar with colors
    std::stringstream ss;
    ss << "\x1b[36m";
    for (int i = 0; i < filled; ++i) ss << "━";
    ss << "\x1b[90m";
    for (int i = 0; i < empty; ++i) ss << "─";
    ss << "\x1b[0m";
    return ss.str();
}

std::string TerminalUI::get_status_icon(const std::string& status) {
    if (status == "Playing") return "▶";
    if (status == "Paused") return "⏸";
    return "⏹";
}

std::string TerminalUI::get_status_color(const std::string& status) {
    if (status == "Playing") return "\x1b[32m";  // Green
    if (status == "Paused") return "\x1b[33m";   // Yellow
    return "\x1b[31m";  // Red
}

std::string TerminalUI::truncate(const std::string& text, int max_length) {
    if (static_cast<int>(text.length()) <= max_length) {
        return text;
    }
    return text.substr(0, max_length - 3) + "...";
}

std::string TerminalUI::strip_ansi(const std::string& text) {
    std::regex ansi_pattern("\x1b\\[[0-9;]*[mGKHfJ]|\x1b_G[^\\\\]*\x1b\\\\");
    return std::regex_replace(text, ansi_pattern, "");
}

int TerminalUI::display_width(const std::string& text) {
    // Calculate actual display width using wcwidth for proper Unicode handling
    std::string clean_text = strip_ansi(text);
    
    int total_width = 0;
    size_t i = 0;
    
    while (i < clean_text.size()) {
        // Decode UTF-8 character
        wchar_t wc;
        int bytes = 1;
        
        unsigned char c = clean_text[i];
        
        if (c < 0x80) {
            // ASCII - 1 byte
            wc = c;
            bytes = 1;
        } else if ((c & 0xE0) == 0xC0 && i + 1 < clean_text.size()) {
            // 2-byte UTF-8
            wc = ((c & 0x1F) << 6) | (clean_text[i + 1] & 0x3F);
            bytes = 2;
        } else if ((c & 0xF0) == 0xE0 && i + 2 < clean_text.size()) {
            // 3-byte UTF-8
            wc = ((c & 0x0F) << 12) | 
                 ((clean_text[i + 1] & 0x3F) << 6) | 
                 (clean_text[i + 2] & 0x3F);
            bytes = 3;
        } else if ((c & 0xF8) == 0xF0 && i + 3 < clean_text.size()) {
            // 4-byte UTF-8
            wc = ((c & 0x07) << 18) | 
                 ((clean_text[i + 1] & 0x3F) << 12) | 
                 ((clean_text[i + 2] & 0x3F) << 6) | 
                 (clean_text[i + 3] & 0x3F);
            bytes = 4;
        } else {
            // Invalid UTF-8, skip
            i += 1;
            continue;
        }
        
        // Use wcwidth to get the display width
        int char_width = wcwidth(wc);
        
        // wcwidth returns -1 for non-printable characters, 0 for zero-width,
        // 1 for normal width, and 2 for wide characters (CJK, emoji, etc.)
        if (char_width < 0) {
            // Non-printable or control character, treat as width 0
            char_width = 0;
        }
        
        total_width += char_width;
        i += bytes;
    }
    
    return total_width;
}

std::vector<std::string> TerminalUI::center_content_vertically(
    const std::vector<std::string>& content_lines) 
{
    // Calculate vertical centering to match artwork height
    int target_height = artwork_height_ + ARTWORK_BORDER_HEIGHT;
    int content_height = content_lines.size();
    
    // Calculate padding needed to center content
    int total_padding = std::max(0, target_height - content_height);
    int top_padding = total_padding / 2;
    int bottom_padding = total_padding - top_padding;
    
    // Build final lines with vertical centering
    std::vector<std::string> lines;
    for (int i = 0; i < top_padding; ++i) {
        lines.push_back("");
    }
    lines.insert(lines.end(), content_lines.begin(), content_lines.end());
    for (int i = 0; i < bottom_padding; ++i) {
        lines.push_back("");
    }
    
    return lines;
}

std::vector<std::string> TerminalUI::render_track_info(
    const std::optional<TrackMetadata>& metadata, int artwork_width) 
{
    if (!metadata) {
        return render_no_player(artwork_width);
    }
    
    const auto& md = *metadata;
    int left_width = term_width_ - artwork_width - 4;
    
    // Build content lines (without vertical padding)
    std::vector<std::string> content_lines;
    
    // Title (bold and colored) with decorative elements
    std::string title_text = truncate(md.title, left_width - 8);
    content_lines.push_back("  ♪ \x1b[1m\x1b[35m" + title_text + "\x1b[0m");
    content_lines.push_back("");
    
    // Artist with icon
    std::string artist_text = truncate(md.artist, left_width - 8);
    content_lines.push_back("  👤 \x1b[36m" + artist_text + "\x1b[0m");
    content_lines.push_back("");
    
    // Album with icon
    std::string album_text = truncate(md.album, left_width - 8);
    content_lines.push_back("  💿 \x1b[90m" + album_text + "\x1b[0m");
    content_lines.push_back("");
    content_lines.push_back("");
    
    // Status with icon
    std::string status_icon = get_status_icon(md.status);
    std::string status_color = get_status_color(md.status);
    content_lines.push_back("  " + status_color + status_icon + " " + md.status + "\x1b[0m");
    content_lines.push_back("");
    content_lines.push_back("");
    
    // Progress bar
    int bar_width = std::min(50, left_width - 4);
    std::string progress_bar = create_progress_bar(md.position, md.length, bar_width);
    content_lines.push_back("  " + progress_bar);
    content_lines.push_back("");
    
    // Time stamps
    std::string current_time = format_time(md.position);
    std::string total_time = format_time(md.length);
    std::string time_str = current_time + " / " + total_time;
    content_lines.push_back("  \x1b[90m" + time_str + "\x1b[0m");
    
    // Center content vertically to match artwork height
    return center_content_vertically(content_lines);
}

std::vector<std::string> TerminalUI::render_no_player(int artwork_width) {
    // Build content lines
    std::vector<std::string> content_lines;
    content_lines.push_back("  \x1b[90mNo active media player found\x1b[0m");
    content_lines.push_back("");
    content_lines.push_back("  \x1b[90mStart playing music and run bass-senpai again\x1b[0m");
    
    // Center content vertically to match artwork height
    return center_content_vertically(content_lines);
}

std::string TerminalUI::render_split_layout(
    const std::vector<std::string>& left_panel,
    const std::vector<std::string>& right_panel) 
{
    std::vector<std::string> left_lines = left_panel;
    std::vector<std::string> right_lines = right_panel;
    
    // Pad to same height
    size_t max_height = std::max(left_lines.size(), right_lines.size());
    while (left_lines.size() < max_height) {
        left_lines.push_back("");
    }
    while (right_lines.size() < max_height) {
        right_lines.push_back("");
    }
    
    // Calculate widths dynamically
    int artwork_width = artwork_width_ + 2;
    int left_width = term_width_ - artwork_width - 2;
    
    std::stringstream output;
    for (size_t i = 0; i < max_height; ++i) {
        const auto& left = left_lines[i];
        const auto& right = right_lines[i];
        
        // Calculate actual display width (accounting for wide characters like emojis)
        int left_visible_width = display_width(left);
        
        // Pad left to fill width
        int left_padding = left_width - left_visible_width;
        std::string left_padded = left;
        if (left_padding > 0) {
            left_padded += std::string(left_padding, ' ');
        }
        
        output << left_padded << "  " << right;
        if (i < max_height - 1) {
            output << "\n";
        }
    }
    
    return output.str();
}

void TerminalUI::display(const std::string& content) {
    // Move to home position
    std::cout << "\x1b[H";
    
    // Write content
    std::cout << content;
    
    // Clear to end of screen
    std::cout << "\x1b[J";
    
    std::cout << std::flush;
    
    last_output_ = content;
}

} // namespace bass_senpai
