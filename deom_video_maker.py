import cv2
import time
import numpy as np

# 輸出影片的設定
output_file = 'output.mp4'
fps = 30  # 設定輸出影片的幀率
# frame_width = 1920  # 輸出影片寬度
# frame_height = 1080  # 輸出影片高度
frame_width = 2700
frame_height = int(1080 / 1920 * 900)

# 空白寬度
padding = 100


class TimerPrinter:

    def __init__(self):
        self.timer_font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.font_thickness = 2
        self.font_color = (0, 255, 0)  # 綠色
        self.fond_color_end = (0, 255, 255)

    def print_timer(self, t, frame, end=False):
        timer_text = "{:.2f} sec".format(t)

        frame_height, frame_width = frame.shape[0], frame.shape[1]

        font_color = self.fond_color_end if end else self.font_color
        text_size, _ = cv2.getTextSize(timer_text, self.timer_font, self.font_scale, self.font_thickness)
        text_x = frame_width - text_size[0] - 10  # 10px 边距
        text_y = frame_height - 10  # 10px 边距

        frame[-40:, -text_size[0] - 30:, :] = 0  # right bottom black box
        frame = cv2.putText(frame, timer_text, (text_x, text_y), self.timer_font, self.font_scale, font_color,
                            self.font_thickness)

        return frame


if __name__ == "__main__":

    file_paths = [
        r"Trim/manual.mp4",
        r"Trim/auto.mp4",
        r"Trim/autoheadless.mp4",
    ]
    caps = [cv2.VideoCapture(fp) for fp in file_paths]

    sub_width = frame_width // len(caps)

    for fp, cap in zip(file_paths, caps):
        if not cap.isOpened():
            print(f"Failed to open video: {fp}")
            exit()

    frame_counts = [int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) for cap in caps]
    frame_rates = [cap.get(cv2.CAP_PROP_FPS) for cap in caps]
    durations = [frame_count / frame_rate for frame_count, frame_rate in zip(frame_counts, frame_rates)]

    for fp, duration in zip(file_paths, durations):
        print(f"Processing video {fp}, Duration: {duration:.2f} seconds")

    # 建立 VideoWriter
    true_frame_width = frame_width + padding * (len(caps)-1) # with padding space
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (true_frame_width, frame_height))
    timer_printer = TimerPrinter()

    t0 = time.time()
    latest_frames = [None for _ in range(len(caps))]
    ends = [None for _ in range(len(caps))]

    frame_index = 0
    while True:

        if frame_index != 0 and not any(rets):
            break

        rets = []
        empty_frame = np.full((frame_height, true_frame_width, 3), 255, dtype=np.uint8)

        # 計算計時器的時間
        elapsed_time = min(frame_index / frame_rates[-1], durations[-1])

        for icol, (cap, end) in enumerate(zip(caps, ends)):
            ret, frame = cap.read()
            rets.append(ret)

            xleft, xright = icol * (sub_width+padding), min((icol+1) * sub_width + icol * padding, true_frame_width)

            if not ret:
                if end is None:
                    ends[icol] = elapsed_time
                    latest_frames[icol] = latest_frames[icol] // 2
                    latest_frames[icol] = timer_printer.print_timer(ends[icol], latest_frames[icol], end=True)
                empty_frame[:, xleft:xright, :] = latest_frames[icol]
                continue

            frame = cv2.resize(frame, (sub_width, frame_height))
            frame = timer_printer.print_timer(elapsed_time, frame)
            latest_frames[icol] = frame # backup latest frame

            empty_frame[:, xleft:xright, :] = frame

        frame_index += 1

        out.write(empty_frame)

        print(frame_index)

    for cap in caps:
        cap.release()
    out.release()
    print(f"Video saved to {output_file}")