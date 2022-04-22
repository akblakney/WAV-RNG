# WAV-RNG
## Introduction
Generating truly random numbers is hard. By definition, computers cannot generate random numbers since they are deterministic in nature. Instead, computers can generate *pseudorandom* numbers. Pseudorandom number generators (PRNGs) use algorithms that take a seed, or starting value, and generate sequences of numbers that approximate the (statistical) properties of sequences of random numbers. Some of these are quite good, and are used for cryptographic purposes, but they cannot be said to be *true* random number generators (TRNGs, or just RNGs). 

While PRNGs generate sequences of numbers that look random, but are in fact predetermined by the algorithm and seed, RNGs generate random numbers based on physical phenomena that are expected to be random. Examples include measuring atmospheric noise, thermal noise, and radioactive decay. In this project, we will use the former as a basis of our random number generator. Specifically, this project includes code that generates random numbers, in a variety of different formats, from .wav files containing recorded atmospheric noise. 

The rest of this document is broken up into __ sections. In the first, I give an overview of how to use the RNG driver program, `rng.py`, to generate random numbers from .wav files containing recorded atmospheric noise. Next, in the second section, I describe the methodology for the RNG in more detail. In the third section, I discuss the testing of the RNG. Finally, I end with some concluding remarks and areas of future improvement.

## Using `rng.py`
(In addition to this section, this information is available in a more condensed form which you can access by running `python3 rng.py -h`. )

Running the `rng.py` script to generate random numbers is very simple. For the most basic usage, you can run `python3 rng.py --in <input.wav>` for any input .wav file. This will print out, as a Python `bytearray`, all the random bytes generated by the .wav file. For a more readable format, you can choose from the `--ascii`, `--binary`, `--hex`, or `--digits` options to get the data in a more readable format. See examples below:

`$ python3 rng.py --in noise.wav --ascii`
output: `CfqGbj[LMa^{lK[{AA`

`$ python3 rng.py --in noise.wav --digits`
output: `60072664111942976`.

To write output to a file, you can run with the `--out` option, followed by a filename:
`$ python3 rng.py --in noise.wav --digits --out random_digits.txt`

The same can be done with any format, including raw bytes, which is the default mode of output.

Often times, a user may have a large .wav file, but may want only a portion of the random data in can generate. Firstly, to check how much random data a .wav file can generate, run,
`$python3 rng.py --in noise.wav -q`.
This runs the "query" function, which will return how many available bytes can be generated:
output: `total available bytes for noise.wav with bpb=16: 8975839`.

This tells us that our file `noise.wav` can generate about 9MB of random data. (Don't worry about the "bpb" part yet. More on that below). 

Now suppose, we want only a fraction of those raw bytes. We can specify the starting and ending bytes to print with the `-s` and `-e` flags. Start is inclusive, while end is exclusive. In mathematical notation, the range: [start, end). Without specifying either, the start position defaults to zero, and the end position defaults to the maximum given the file-size):
`$python3 rng.py --in noise.wav -s 10 -e 14 --hex`
output: `a06b1aa4`. (Note that only four bytes, in the form of hexadecimal digits, were printed out).

The above examples conclude the most basic functionality of the RNG. For the remaining steps, we will have to dive into the more technical aspects of how the random number generation happens. For a full description of the technical details, see the ~Methodology and Technical Details ~ section. But for now I will go over the basics in order to demonstrate the other options for `rng.py`

### -bpb: `bits_per_block`
Again, the full technical details of the RNG are described in the next section, but for the sake of this section, the `bits_per_block` variable dictates how many bits make up a larger "block" in the .wav file. Instead of taking all the data from the .wav file and passing it off as random data, only one bit per each block of .wav data is selected to be output in the stream of generated random data. There are technical reasons for this, as described in the next section, and the default value of `bits_per_block=16` is probably sufficient unless you're interested enough to mess around with it yourself.

### -u: `use_bit`
This variable dictates which bit, within each block of .wav data, should be used. The default value is set to `None`, which means that all bits in each block will be XOR-ed together. Alternatively, the user could use `0`, as .wav data is stored in little-endian, and therefore the least significant bit will be used. The default value of `None` should be sufficient.

### Combining with pseudorandom data
`rng.py` provides the option of combining the random data generated from the .wav file with pseudorandom data from different sources. The two sources that are currently available are the Python secrets module, with associated flag `--secrets` and pseudorandom data generated from grc.com/passwords.htm (Gibson Research Corporation) with `--grc`. Additionally, both can be selected, and all three sources of (pseudo)randomness will be used. The method of combining the random data is with the XOR function, which is discussed in more detail in the next section. Also note that, when using `--grc`, a maximum of 32 bytes can be requested, as getting larger amounts of data would require spam-requesting the site which I do not want to encourage. Examples:

`$ python3 rng.py --in noise.wav -s 0 -e 6 --secrets --hex`
output: `ae2f0ae08656`

Also, you can choose to run `rng.py` without a .wav file at all! (Although this kind of defeats the purpose of this project...). When doing this, however, you will need to specify the number of bytes, and you will have to choose the secrets and/or grc modes:

`$python3 rng.py --secrets --num_bytes 10 --digits`.

## Methodology and Technical Details
### Intuition
The methodology for this RNG was greatly inspired by Jeremy Triplett in his [medium post](https://jeremytriplett06.medium.com/using-atmospheric-noise-to-generate-true-random-numbers-dc820ac9452d) on the topic. As such, anyone who is interested in my methodology should read his overview. Additionally, his provided links to information about the [WAV](http://soundfile.sapp.org/doc/WaveFormat/) file format will be useful to anyone pursuing a similar project, or just trying to understand the details here. Another resource worth mentioning is random.org, a site that provides random data generated by atmospheric noise free of charge (up to a point). The site also has plenty of good reading material about randomness and the statistics of it all.

The basic idea behind the RNG is this: the waveform of [atmospheric noise](https://en.wikipedia.org/wiki/Atmospheric_noise), which is after all radio noise caused by natural atmospheric processes, should be random. The way that this waveform is captured in a .wav file is by a series of 16-bit samples. Basically, the data of a .wav file is a series of 16-bit numbers that describe the wave at different points in time. 

You might think that since the waveform of atmospheric noise looks pretty random, and the .wav data essentially captures that waveform in a series of 16-bit integers, we can just take all the data in the .wav file and pass it off as random. This is problematic, however, due to the way binary encoding works. In particular, since these integers are encoded in binary, some of the bits are more significant than others and are bound to vary more than others in subsequent samples of the .wav file. (Another probed when use_bit=None is used. This lends credence to my suspicion that this is the best mode of operation, hence it being the default mode lem is the fact that .wav files have a 44-byte header. But this is easily remedied by simply skipping over those bytes).

To understand this, consider an example. Suppose we are measuring some sort of physical quantity over time. At a certain time, `t_0`, the quantity takes on the value 7378267 units. Over a short period of time, until, say `t_1`, we expect the quantity to vary randomly in some direction, but the magnitude of that variation might not be very big. As an example, for a series of times, we might measure 7378382 units, then 7412868, then, 7351467, and so on. The variation from each sample to the next seems random, and yet the numbers taken in their entirety don't: namely because they don't vary enough to change the most significant digit (7), and hardly the second most significant digit (it changed from 3 to 4 and back to 3). 

The same concept applies with the waveform of our atmospheric noise. The most significant digit in the binary encoding is not likely to change very much (and therefore, not a very good source of randomness) from sample to sample. The least significant digit, however, we can assume to be quite random, since the variation from one sample to the next dwarfs the magnitude of the least significant bit (which is 1 in binary). Therefore, from each 16-bit sample, we will only grab the least significant bit and add it to our randomly generated sample. We can also think of this least significant bit as an indicator of whether the waveform is even or odd at a given point in time. Since we are dealing with such large magnitudes (16 bits gives a total magnitude of 2^16, which is over 60,000), whether the waveform at a given point in time is even or odd should be random.

### `bits_per_block` and `use_bit`

This is where the `bits_per_block` variable mentioned earlier in this document fits in. The default value is set to 16 bits, which means that one bit per every 16-bit integer in the .wav file is taken as a random bit. Users can specify a larger value for this variable, as long as it is a multiple of 16, to essentially skip over different blocks. For example, setting `-bpb 32` sets the `bits_per_block` variable to 32, which means that now we are only extracting one random bit from every *two* 16-bit integers in the .wav file. As mentioned earlier, if the `use_bit` variable is not set, all of these 32 bits will be XOR-ed together to produce our random bit. If a value between 0 and 32—i.e., [0, 32)—is chosen, then that bit will be used in every group of 32 bits in the .wav file. Therefore, setting `-bpb 32 -u 0` would use the 0th bit of every other 16-bit integers in the .wav file as a random bit.

### The *Exclusive or* operation
[Exclusive or](https://en.wikipedia.org/wiki/Exclusive_or), or XOR, is a logical operation that we can perform on two bits, or strings of bits of any length. Interested readers should take a look at the linked Wikipedia page for more details, but basically, the XOR of two bits is 1 if and only if the bits differ. That is, if two bits `a` and `b` are the same (both 0 or both 1), the XOR of `a` and `b` is 0; if they are different (one is 1 and the other is 0), their XOR is 1. 

This logical operation is relevant for us because it has some useful properties when it comes to randomness. Namely, the XOR operation preserves randomness. This means that, if I have a string of random bits (that is, generated from a random process, such that each bit is 1 with probability 0.5 and 0 with probability 0.5), and I XOR that string of bits with *any* (statistically independent) string of bits of the same length, the resulting string of bits will also be random. XOR is quite a powerful tool then: even if I XOR a string of random bits with a completely deterministic and non-random string of bits (say 11111..., i.e. a string which entirely consists of 1s), the result will still be random! There is one caveat that I mentioned above, which is that the two strings must be statistically independent, i.e., their probability distributions cannot depend on one another. Luckily, the way we are using XOR in this project adheres to this requirement.

In the previous section I talk about the `--secrets` and `--grc` options which allow the user to combine the random bits generated from the .wav file with pseudorandom bits generated in the Python secrets module and GRC's PRNG. The reason I provide this option is to increase the robustness of the RNG overall. Consider the idea that we may not be completely sure that the bits generated from the .wav files are entirely random. Perhaps the frequency we are tuning to during the recording process has a faint signal that has a pattern to it. Or perhaps the way that the waveform is being written to the .wav file has some properties that causes some patterns of bits to be more likely than others. In most instances this seems unlikely given the testing I have done on the .wav portion of the RNG, which I describe in more detail in the next section, but it is always a possibility. The option of combining the random data from the .wav portion of the RNG with other sources of pseudorandom data is a way to counter this possibility. 

As I mentioned, as long as two strings of bits are statistically independent—and here it is safe to say that the .wav data, the output of the Python secrets module, and the output of the GRC PRNG are mutually independent, satisfying this requirement—XOR-ing these bit strings together cannot eliminate any randomness that either of the bit strings already contained. In other words, if we XOR random data generated from the .wav file with pseudorandom data generated from the Python secrets module, the output will still be "just as random" as the data from the .wav file. I put "just as random" in quotes because talking about *how random* something is perhaps requires more mathematically robust language than is being used here, but the overall principle holds.

So the gist of it is, XOR-ing the random output from the .wav file with pseudorandom data from the Python secrets module (which Python claims is a cryptographically-secure pseudorandom generator (CSPRNG)) cannot "downgrade" the randomness of the data. It can only upgrade it in the event that the .wav portion of the RNG isn't functioning properly and is not working as a proper RNG. In this instance, we would be XOR-ing non-random data from the .wav generator with pseudrandom data from Python's secrets module, and we would essentially have a PRNG. So users can view this option as a sort of fail-safe against the hard-to-eliminate possibility that the .wav RNG has some imperfections. 

## Testing

### Nist Randomness Test Suite
In this section I discuss the results of NISTS *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications* applied to the output of my RNG. You can find the official posting of this project by NIST [here](https://www.nist.gov/publications/statistical-test-suite-random-and-pseudorandom-number-generators-cryptographic), which has a link to download the PDF of their document. For this project I used [this](https://github.com/stevenang/randomness_testsuite) implementation of the NIST test suite by Steven Kho Ang and Spence Churchill. For anyone looking for an implementation of the test suite, I recommend theirs as it was easy to get running and very user-friendly with GUI and command-line options.

Readers who are interested in the testing of RNGs should take a look at NIST's own document, or do some googling about it. But the gist of the tests is rather simple. They use a hypothesis testing aproach, with p-values. In each test, the data is treated as if it were random (i.e., the null hypothesis is that the data is random). Then, various test statistics are computed based on that data, and if the resulting p-value is sufficiently low, the null hypothesis is rejected and the data is deemed "non-random." This is a slight oversimplification, but the overall principle is true: treat the data as if it were random, and if the results are sufficiently unlikely, the null hypothesis is rejected and the data is deemed non-random.

To test the .wav portion of the RNG, I generated ten files containing 1MB of randomd data. This particular implementation takes in files with binary strings, so the actual files were 8MB in size, but the actual data being tested in each was 1MB. To generate these six files, I used five .wav files recorded at separate times. For each .wav file, I generated 1MB of data using a `use_bit` value of `None` (i.e., XOR all bits in each 16-bit block together) and another 1MB of data using a `use_bit` value of `0` (i.e., use the 0th bit in each 16-bit block of .wav data). I then rand all tests in the test suite on each file independently. Reports on all ten of these files are available in the `results/NIST/` section.

There are a total of 16 tests, but some of them have multiple portions of the tests, each with their own results. In total then, there are 41 p-values given. I thus consider the test to output 41 separate p-values, which are interpreted as pass/fail (random/non-random) according to the thresholds recommended by NIST. Of the ten 1MB files tested, all but two passed all tests. One of the files that failed at least once failed five tests, and had extremely low p-values. This is a strong indication that the data in this file was not generated by a random process. The other file that failed at least one test only failed one test out of the 41, and the p-value of failure was 0.005 which is well within the realm of probability. It is worth remembering that even if the data was random, a p-value less than or equal to 0.005 would occur at exactly that rate, i.e. one in every 200 times. Given that we are testing ten files, each 41 times for a total of 410 tests, even a couple of p-values at around this value would be expected. Also, Python's secrets PRNG failed one test as well, which gives us a good benchmark for what is to be expected.

The below table summarizes the results. The first column gives the test iteration (five total sets of tests, each set with 41 tests within it). The second and third columns give the number of failures for each mode of operation (`use_bit=0` and `use_bit=None`). And the last column gives the results on Python's secrets PRNG as a control and point of reference. Recall that in each instance, a total of 41 tests is being run, so the number of failures should be understood in this context.

| Test iteration | `use_bit=0` failures | `use_bit=None` failures| secrets failures |
| ----------- | -------------------- | ---------------------- | ------------- |
| 0           |     5 | 0 | 1 |
| 1 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 |
| 3 | 1 | 0 | 0 |
| 4 | 0 | 0 | 0 |

It is also worth noting that no failures occured when `use_bit=None` is used. This lends credence to my suspicion that this is the best mode of operation, hence it being the default mode when no `-u` is specified. Thus, with `use_bit=None`, the .wav RNG performed just as well, if not better, than the Python's secrets module did. With `use_bit=0`, the .wav RNG generated one file of which there is a strong indication that the data is not random, and four other files that are quite plausibly generated by a random process. (Again, one test failure out of 4 * 41 = 164 tests is not very strong evidence that the generator is not strong).

As for the file with 5 failures and extremely low p-values, it is curious why it failed so definitively. I had done plenty of NIST's tests on data generated by the RNG during development, and had not seen a failure rate this high. At most, I had seen one test out of the 41 tests fail, but the vast majority of the time no tests failed. Furthermore, I had never seen p-values so low—some as low as 1e-27, an extremely small number that gives a strong indication of non-randomness. While I can not be sure what caused this, I believe that, given the other test results (both NIST randomness test suite and others discussed in this section), these results are an anomoly. Perhaps during the recording process a signal with a pattern was active, or there was some other error with handling the data. Additionally, I had noticed during development that sometimes the beginning portion of .wav files was not so random (e.g., the files contained a lot of zeros at the beginning). This too could have been a contributing factor. That said, I believe it is important to conduct this testing honestly and scrupulously, so I have kept these results in. This incident may also serve as a reminder of a suggested practice when generating nrandom numbers in this manner: regular testing of this sort should be used to test for biases in the measuring process, and to verify that numbers generated from processes which are expected to be random are indeed random.

In the future I would like to collect large amounts of atmospheric noise data so that I can continue the testing process with this test suite. This could help ascertain with more certainty whether the five failures for one of the files is an anomaly or a larger problem with the RNG. In conclusion, the extremely small p-values in one of the NIST tests is worrying, and a strong indication that that data was not generated by a random process. However, in conjunction with the other tests I have done, it is difficult to make any broad conclusions about the RNG. In my personal interpretation, given the other test results, those small p-values seem like they were caused by an anamoly in the atmospheric noise recording process, but do not invalidate the effectiveness of the RNG overall, as long as proper care is taken to ensure that the recording process is administered properly and proper testing is done to confirm the RNG's effectiveness. Furthermore, none of the results indicate a failure of the `use_bit=None` mode, perhaps indicating that this method is robust enough to overcome anamolous data that would otherwise introduce non-randomness as with the `use_bit=0` case.

### ENT: Pseudorandom Number Sequence Test Program
In this section I apply the [ent](https://www.fourmilab.ch/random/) sequencing program on data generated by the .wav RNG. This testing program is not as rigorous as the NIST suite, and is not based on hypothesis testing or p-values. Instead, it outputs a brief summary of various test statistics and makes no adjudication on whether the data seems randomly generated or not.

I used the ent program on the same files as in the NIST test suite. The full results are available in `results/ent/`, and an example of one output is below:

```
Entropy = 7.999820 bits per byte.

Optimum compression would reduce the size
of this 1000000 byte file by 0 percent.

Chi square distribution for 1000000 samples is 250.05, and randomly
would exceed this value 57.57 percent of the times.

Arithmetic mean value of data bytes is 127.5314 (127.5 = random).
Monte Carlo value for Pi is 3.139788559 (error 0.06 percent).
Serial correlation coefficient is -0.000203 (totally uncorrelated = 0.0).
```

Most of the other ent results look similar. A full description of the fields of the test is available at the linked site, but briefly: 
- entropy gives the information density of the file. A perfect score is 8 bits per byte, and the 7.999820 is quite close.
- Optimum compression gives how much the file could be compressed. Random data should not be able to be compressed at all, normally, since there should be very little detectable pattern in the data. The above result indicates 0% compression is possible, which is a perfect score. 
- The Chi squared test statistic is, according to the authors, "extremely sensitive to errors in pseudorandom sequence generators ... If the percentage is greater than 99% or less than 1%, the sequence is almost certainly not random..." In short, extreme values indicate non-randomness, so a score of 58% is good.
- Arithmetic mean is simply the result of summing the bytes and computing an average. The [law of large numbers](https://en.wikipedia.org/wiki/Law_of_large_numbers) tells us that for large sequences of random numbers, this statistic should converge to the true mean, in this case 127.5. Scores close to this value are to be expected, whereas scores that stray far from this value could indicate non-randomness.
- The Monte Carlo value for Pi section uses the data to approximate Pi via the [Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method). If a large sequence of data has a very inaccurate Monte Carlo approximation it is an indication that the data is not random. Our small error of 0.06% is well within the expected value of random data.
- Serial correlation tells us how much subsequent bytes depend on each other. For random data, this should be very close to zero.

As I mentioned, this is not a very rigorous test, but can serve as a sanity check that our generator is performing decently.
