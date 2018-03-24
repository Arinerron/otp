Examples:

    To encrypt:
        
        $ echo "Your message here..." | python3 otp.py -e > output.txt
        $ python3 otp.py -i +1
        
        ...then send output.txt to whoever you want.
        
    To decrypt:

        ...write the ciphertext (encrypted message) to output.txt

        $ cat output.txt | python3 otp.py -d
        $ python3 otp.py -i +1
    
What is the -i/--index option?

    It is very important never to reuse keys. So, this script works by having a precomputed list of keys. Each key is only used once. The -i/--index option simply increments the index of the key in the list of keys by whatever value is following. For example, `python3 otp.py -i +1` would move to the next key, while `python3 otp.py -i -1`.
    
    The script will automatically try to identify the index. However, in cases where that is not possible or when something messes up, you can change the offset using the -i/--index option.