if __name__ == "__main__":
    from patches import Patch, SineGenerator, AudioOutput, MouseData, ChromaticFrequencyStepper, VCA,AccAndDec, WavePlayer,Printer
    from patches.waveforms import FunctionWave
    from Board import Board
    
    # Create patches
    mouse = MouseData()
    chrom = ChromaticFrequencyStepper()
    sine_gen = SineGenerator(frequency=440, amplitude=0.3)
    sine_gen2 = SineGenerator(frequency=110/16, amplitude=0.3)
    audio_out = AudioOutput(blocksize=512)
    vca = VCA(amplification=2)
    acc = AccAndDec()
    form  = FunctionWave(lambda x: -4.0*x*(x-1.0),duration=0.5)
    wav = WavePlayer(form)
    prin = Printer(interval=10000)
    
    # Create board and add patches
    board = Board(patches=[sine_gen, sine_gen2, audio_out,chrom,mouse,vca,wav])
    print(sine_gen.inputs,sine_gen.outputs)
    print(audio_out.inputs,audio_out.outputs)
    # Connect the sine generator to the audio output
    
    Patch.connect(wav,mouse,"input","mouseScroll")
    #Patch.connect(prin,wav,"input","output")
    Patch.connect(sine_gen,wav,"amplitude","output")
    Patch.connect(chrom,mouse,"input","mouseX")
    Patch.connect(sine_gen,chrom,"frequency","output")
    Patch.connect(vca,sine_gen,"input","output")
    Patch.connect(vca,sine_gen2,"amplification","output")
    Patch.connect(audio_out, vca, "input", "output")
    
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