if __name__ == "__main__":
    from patches import Patch, SineGenerator, AudioOutput, MouseData, WavePlayer, Printer
    from patches.waveforms import FileWave, FunctionWave
    from Board import Board
    
    # Create patches
    mouse = MouseData()
    
    audio_out = AudioOutput(blocksize=512)
    form = FileWave("data/waves/record_out.wav")
    wav = WavePlayer(form)
    sine_gen = SineGenerator(frequency=1/18, amplitude=len(form))
    prin = Printer(interval=10000)
    # Create board and add patches
    board = Board(patches=[sine_gen,  audio_out, mouse,wav,prin])
    
    # Connect the sine generator to the audio output
    
    Patch.connect(prin,sine_gen,"input","output")
    Patch.connect(wav,prin,"play_progress","output")
    Patch.connect(wav,mouse,"input","mouseX")
    Patch.connect(audio_out, wav, "input", "output")
    


    try:
        # Start the audio stream
        board.play()
        
        # Keep the program running until interrupted
        input("Press Enter to stop...")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    
    finally:
        # Ensure the stream is stopped
        board.stop()