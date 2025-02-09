import tkinter as tk
import random
import time
from datetime import datetime, date

class BlockMemoryGameSequence(tk.Tk):
    def __init__(self, 
                 grid_size=4, 
                 initial_sequence_length=3,
                 initial_level=1):
        super().__init__()
        
        self.title("Block Memory Game (Fixed Sequence + Daily/Monthly Performance + Streak)")

        # --- Game Settings ---
        self.grid_size = grid_size
        self.level = initial_level
        self.initial_sequence_length = initial_sequence_length
        
        # Colors
        self.default_color = "lightgray"
        self.highlight_color = "red"
        self.correct_select_color = "green"
        self.wrong_select_color = "yellow"
        
        # Game State
        self.buttons = []                # 2D list of buttons
        self.correct_sequence = []       # Ordered list of (row, col)
        self.sequence_index = 0          # Next position in the sequence
        self.showing_sequence = False    # Flag to ignore clicks while showing

        # Performance / Stats
        self.round_start_time = None
        self.replay_count = 0
        self.performance_data = []       # List of dicts, each storing round info
        self.current_streak = 0         # Count of consecutive successful rounds
        self.longest_streak = 0         # Track the maximum streak ever reached
        
        # Create the UI
        self.create_widgets()
        
        # Start the first round
        self.start_new_round()
    
    def create_widgets(self):
        """Create grid buttons, message label, and control buttons."""
        # Create the grid of buttons
        for row in range(self.grid_size):
            row_buttons = []
            for col in range(self.grid_size):
                btn = tk.Button(
                    self, 
                    width=6, 
                    height=3, 
                    bg=self.default_color,
                    command=lambda r=row, c=col: self.on_block_click(r, c)
                )
                btn.grid(row=row, column=col, padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        # Message label
        self.message_label = tk.Label(self, text="", font=("Helvetica", 12))
        self.message_label.grid(row=self.grid_size, column=0, columnspan=self.grid_size, pady=(10, 0))
        
        # "Next Round" button
        self.next_button = tk.Button(self, text="Next Round", command=self.start_new_round, state="disabled")
        self.next_button.grid(row=self.grid_size+1, column=0, columnspan=self.grid_size, pady=5)
        
        # "Show Pattern Again" button
        self.show_pattern_button = tk.Button(self, text="Show Pattern Again", command=self.show_pattern_again, state="disabled")
        self.show_pattern_button.grid(row=self.grid_size+2, column=0, columnspan=self.grid_size, pady=5)
        
        # "Show Performance" button
        self.performance_button = tk.Button(self, text="Show Performance", command=self.show_performance)
        self.performance_button.grid(row=self.grid_size+3, column=0, columnspan=self.grid_size, pady=5)
    
    def start_new_round(self):
        """Setup a new round: pick the sequence, show it, reset tracking variables."""
        self.sequence_index = 0
        self.showing_sequence = True
        self.replay_count = 0
        self.next_button.config(state="disabled")
        self.show_pattern_button.config(state="disabled")
        
        # Record round start time
        self.round_start_time = time.time()
        
        # Reset all buttons
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.buttons[row][col].configure(bg=self.default_color, state="disabled")
        
        self.message_label.config(text=f"Level {self.level}: Watch the sequence...")
        
        # Decide how many blocks in the sequence for this level
        total_cells = self.grid_size * self.grid_size
        sequence_length = min(total_cells, self.initial_sequence_length + (self.level - 1))
        
        # Generate a random sequence
        all_positions = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        self.correct_sequence = random.sample(all_positions, sequence_length)
        
        # Show the sequence to the user
        self.show_sequence_step(0)
    
    def show_sequence_step(self, index):
        """Highlight the block at 'index' in self.correct_sequence, then schedule un-highlighting."""
        if index >= len(self.correct_sequence):
            # Done showing entire sequence
            self.finish_showing_sequence()
            return
        
        # Highlight current block
        (r, c) = self.correct_sequence[index]
        self.buttons[r][c].configure(bg=self.highlight_color)
        
        # After 600 ms, un-highlight and move on
        self.after(1000, lambda: self.hide_sequence_step(index))
    
    def hide_sequence_step(self, index):
        """Un-highlight the block at 'index' and proceed to next."""
        (r, c) = self.correct_sequence[index]
        self.buttons[r][c].configure(bg=self.default_color)
        
        # Short pause before next highlight
        self.after(200, lambda: self.show_sequence_step(index + 1))
    
    def finish_showing_sequence(self):
        """Enable the board for user clicks, allow re-show button."""
        self.showing_sequence = False
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.buttons[row][col].configure(state="normal")
        
        self.message_label.config(text="Click the blocks in the same order.")
        # Now that the sequence has been shown once, allow re-show
        self.show_pattern_button.config(state="normal")
    
    def on_block_click(self, row, col):
        """Check whether user clicked the correct next block in the sequence."""
        if self.showing_sequence:
            # Ignore clicks during sequence display
            return
        
        correct_position = self.correct_sequence[self.sequence_index]
        
        if (row, col) == correct_position:
            # Correct block
            self.buttons[row][col].configure(bg=self.correct_select_color, state="disabled")
            self.sequence_index += 1
            
            # Check if user completed the sequence
            if self.sequence_index == len(self.correct_sequence):
                self.end_round(success=True)
        else:
            # Wrong block/order
            self.buttons[row][col].configure(bg=self.wrong_select_color, state="disabled")
            self.end_round(success=False)
    
    def show_pattern_again(self):
        """Replay the current sequence from the start, incrementing self.replay_count."""
        self.replay_count += 1
        self.showing_sequence = True
        self.message_label.config(text="Replaying the sequence. Watch carefully...")
        
        # Temporarily disable all buttons
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.buttons[row][col].configure(state="disabled")
        
        # Show the sequence again
        self.show_sequence_step(0)
    
    def end_round(self, success):
        """Record performance, disable board, show message, and enable Next Round."""
        # Disable the board
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.buttons[row][col].configure(state="disabled")
        
        # Calculate time taken
        round_end_time = time.time()
        time_taken = round_end_time - self.round_start_time
        
        # Update streak
        if success:
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0  # reset streak on fail
        
        # Append performance data
        # We'll record today's date, plus success/fail, time, replays, streak
        now = datetime.now()
        record = {
            "round": len(self.performance_data) + 1,
            "level": self.level,
            "result": "Success" if success else "Fail",
            "time": time_taken,
            "replays": self.replay_count,
            "date": now.date(),         # e.g., 2025-02-03
            "month_key": now.strftime("%Y-%m"),  # e.g., "2025-02"
            "streak_after_round": self.current_streak
        }
        self.performance_data.append(record)
        
        # Show message
        if success:
            self.message_label.config(text=f"Level {self.level} complete! Well done.")
            self.level += 1
        else:
            self.message_label.config(text=f"Wrong block! You reached Level {self.level}. Restarting at Level 1.")
            self.level = 1
        
        # Enable Next Round, disable re-show
        self.next_button.config(state="normal")
        self.show_pattern_button.config(state="disabled")
    
    def show_performance(self):
        """
        Open a new window to display:
         1) Detailed round-by-round data
         2) Daily summary
         3) Monthly summary
         4) Current streak and longest streak
        """
        perf_window = tk.Toplevel(self)
        perf_window.title("Performance (Daily / Monthly / Streak)")

        # Use a Text widget to display the info
        text_widget = tk.Text(perf_window, width=100, height=30)
        text_widget.pack(padx=10, pady=10)

        # 1) Round-by-Round Header
        text_widget.insert(tk.END, "=== Round-by-Round Details ===\n")
        header = f"{'Round':<6}{'Level':<6}{'Result':<10}{'Time(s)':<10}{'Replays':<8}{'Date':<12}{'Streak':<8}\n"
        text_widget.insert(tk.END, header)
        text_widget.insert(tk.END, "-"*60 + "\n")

        # Populate round-by-round
        for record in self.performance_data:
            line = (
                f"{record['round']:<6}"
                f"{record['level']:<6}"
                f"{record['result']:<10}"
                f"{record['time']:.2f}{' ':<2}"
                f"{record['replays']:<8}"
                f"{record['date']:<12}"
                f"{record['streak_after_round']:<8}\n"
            )
            text_widget.insert(tk.END, line)

        text_widget.insert(tk.END, "\n")

        # 2) Daily Summary
        daily_stats = self._compute_daily_stats()
        text_widget.insert(tk.END, "=== Daily Summary ===\n")
        text_widget.insert(tk.END, f"{'Date':<12}{'Rounds':<8}{'Success':<8}{'Fail':<8}{'AvgTime':<10}\n")
        text_widget.insert(tk.END, "-"*48 + "\n")

        for day_str, stats in daily_stats.items():
            line = (
                f"{day_str:<12}"
                f"{stats['rounds']:<8}"
                f"{stats['success']:<8}"
                f"{stats['fail']:<8}"
                f"{stats['avg_time']:<10.2f}\n"
            )
            text_widget.insert(tk.END, line)

        text_widget.insert(tk.END, "\n")

        # 3) Monthly Summary
        monthly_stats = self._compute_monthly_stats()
        text_widget.insert(tk.END, "=== Monthly Summary ===\n")
        text_widget.insert(tk.END, f"{'Month':<8}{'Rounds':<8}{'Success':<8}{'Fail':<8}{'AvgTime':<10}\n")
        text_widget.insert(tk.END, "-"*42 + "\n")

        for month_key, stats in monthly_stats.items():
            line = (
                f"{month_key:<8}"
                f"{stats['rounds']:<8}"
                f"{stats['success']:<8}"
                f"{stats['fail']:<8}"
                f"{stats['avg_time']:<10.2f}\n"
            )
            text_widget.insert(tk.END, line)

        text_widget.insert(tk.END, "\n")

        # 4) Streak info
        text_widget.insert(tk.END, "=== Streak Info ===\n")
        text_widget.insert(tk.END, f"Current Streak: {self.current_streak}\n")
        text_widget.insert(tk.END, f"Longest Streak: {self.longest_streak}\n")

        text_widget.config(state="disabled")

    def _compute_daily_stats(self):
        """
        Returns a dict keyed by date (string), each value is:
        {
          'rounds': <count_of_rounds>,
          'success': <count_of_success>,
          'fail': <count_of_fail>,
          'avg_time': <average time over that date>
        }
        """
        daily = {}
        for record in self.performance_data:
            day_str = record["date"].isoformat()  # e.g. '2025-02-03'
            if day_str not in daily:
                daily[day_str] = {
                    "rounds": 0,
                    "success": 0,
                    "fail": 0,
                    "total_time": 0.0
                }
            daily[day_str]["rounds"] += 1
            if record["result"] == "Success":
                daily[day_str]["success"] += 1
            else:
                daily[day_str]["fail"] += 1
            daily[day_str]["total_time"] += record["time"]
        
        # Compute average time
        for day_str, stats in daily.items():
            avg_time = stats["total_time"] / stats["rounds"] if stats["rounds"] > 0 else 0
            stats["avg_time"] = avg_time
        
        return daily

    def _compute_monthly_stats(self):
        """
        Returns a dict keyed by 'YYYY-MM', each value is:
        {
          'rounds': <count_of_rounds>,
          'success': <count_of_success>,
          'fail': <count_of_fail>,
          'avg_time': <average time over that month>
        }
        """
        monthly = {}
        for record in self.performance_data:
            m_key = record["month_key"]  # e.g. "2025-02"
            if m_key not in monthly:
                monthly[m_key] = {
                    "rounds": 0,
                    "success": 0,
                    "fail": 0,
                    "total_time": 0.0
                }
            monthly[m_key]["rounds"] += 1
            if record["result"] == "Success":
                monthly[m_key]["success"] += 1
            else:
                monthly[m_key]["fail"] += 1
            monthly[m_key]["total_time"] += record["time"]
        
        # Compute average time
        for m_key, stats in monthly.items():
            avg_time = stats["total_time"] / stats["rounds"] if stats["rounds"] > 0 else 0
            stats["avg_time"] = avg_time
        
        return monthly


if __name__ == "__main__":
    app = BlockMemoryGameSequence(grid_size=7, 
                                  initial_sequence_length=3,
                                  initial_level=1)
    app.mainloop()
