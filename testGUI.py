# test.py (updated)
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from gui.MainWindow import MainWindow
    
    # Create board and patches (same as before)
    from patches import Patch, SineGenerator, AudioOutput, MouseData, WavePlayer, Printer
    from patches.waveforms import FileWave
    from Board import Board
    
    # Create patches
    mouse = MouseData(scaleX=1/2048)
    audio_out = AudioOutput(blocksize=512)
    form = FileWave("data/waves/record_out.wav")
    wav = WavePlayer(form)
    sine_gen = SineGenerator(frequency=1/18, amplitude=len(form))
    prin = Printer(interval=10000)
    
    # Create board and add patches
    board = Board(patches=[sine_gen, audio_out, mouse, wav, prin])
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow(board)
    
    # Run the application
    sys.exit(app.exec_())