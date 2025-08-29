if __name__ == "__main__":
    from Patch import Patch, SineGenerator, AudioOutput
    from Board import Board
    
    # Create patches
    sine_gen = SineGenerator(frequency=440, amplitude=0.3)
    audio_out = AudioOutput(blocksize=512)
    
    # Create board and add patches
    board = Board(patches=[sine_gen, audio_out])
    print(sine_gen.inputs,sine_gen.outputs)
    print(audio_out.inputs,audio_out.outputs)
    # Connect the sine generator to the audio output
    Patch.connect(audio_out, sine_gen, "input", "output")
    
    print(sine_gen.inputs,sine_gen.outputs)
    print(audio_out.inputs,audio_out.outputs)

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