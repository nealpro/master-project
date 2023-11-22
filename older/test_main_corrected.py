import main

def test_loop():
    # Simulate button press
    main.touch_state = True

    # Call loop function and check that it does not exit without an exception
    try:
        main.loop()
    except:
        assert False, "loop function exited with an exception"