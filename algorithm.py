def getRandomSeed(seed):

    print(seed)
    out = []

    end_size = len(seed)
    block_size = 4
    samplesize = 6
    j = 1
    k = 1

    while len(out) < samplesize-1:
        valid = False
        while (not valid):
            nhex = seed[end_size-block_size*j:end_size-block_size*(j-1)]
            nint = divmod(int(nhex,16),50)[1]
            print(out)
            print(nint)
            if nint in set(out):
                valid = False
                j = j + 1
            elif nint == 0:
                valid = False
                j = j + 1
            elif nint not in set(out):
                valid = True
                out.append(nint)
                j = j + 1


    print(j)
    #j = j + 1

    valid=False

    while(not valid):
        valid == False
        nhex = seed[end_size - block_size * j:end_size - block_size * (j - 1)]
        nint = divmod(int(nhex,16), 27)[1]
        if nint == 0:
            valid = False
            j = j + 1
        elif nint != 0:
            valid = True
            out.append(nint)
            j = j + 1

    print(out)
    return out

#Main program which returns the winning numbers (5 Whites and 1 Red)