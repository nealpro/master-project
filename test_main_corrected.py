import main_corrected

def test_loop():
    # Simulate button press
    main_corrected.button_state = True

    # Call loop function and check that it does not exit without an exception
    try:
        main_corrected.loop()
    except:
        assert False, "loop function exited with an exception"