/*
This file as a whole functions as a test file.

Function for chunking bits is processStream(const std::string& filename). This is the function which will be used for the project. 
Searches for the Bit Synchronization Pattern or the Frame Synchronization Pattern in a chunk of 144 bits. If it's found it 
currently prints out the chunk and begins the process again after the end of the next chunk (ex: If bits 1 - 144 are chunked, it 
begins searching at bit 155). This function takes a filename as an input for the FIFO system, this can modified easily to a new 
FIFO input if necessary. It does work if new data is added to the file while the function is running.

WriteBits is a function which just adds the BSP or FSP at random to the text file. This is primarily for testing purposes to ensure
the processStream will identify new data in the FIFO and chunk it. It should not be used in the final product.

Main shows how these functions can be run, I'm unsure if it's necessary to execute them as threads. 2 lines are commented out,
these are the creation and execution of the thread for WriteBits. If you wish to test the files you may uncomment these and
run the file.

Additonally a Python file is included in this folder to preload the text file with bits and the necessary patterns, this is also
for testing purposes.
*/

#include <iostream>
#include <fstream>
#include <thread>
#include <atomic>
#include <string>
#include <chrono>
#include <fcntl.h>    // for open(), O_RDONLY, O_WRONLY
#include <unistd.h>   // for close(), read(), write()
#include <cstring>    // for strncmp

// Function to continuously read bits from the file
void processStream(int infd, int outfd) {
    const char* BSP = "111111111111111";
    const char* FSP = "000101111";

    char current_chunk[144] = {0};
    size_t currLen = 0;
    
    while (true) {
        char bit;
        ssize_t bytes_read = read(infd, &bit, 1);

        if (bytes_read == 1) {  // Read next bit
            if (currLen < 144) {
                current_chunk[currLen++] = bit;
            } else {
                if (strncmp(current_chunk, BSP, 15) == 0) {
                    std::cout << "Pattern 1 detected!\n"; std::cout.write(current_chunk, 144) << std::endl;
                    int bytesWrote = write(outfd, current_chunk, 144);
                    currLen = 0;
                    std::cout << "PacketDetector wrote " << bytesWrote << std::endl;
                } else if (strncmp(current_chunk + 15, FSP, 9) == 0) {
                    std::cout << "Pattern 2 detected!\n"; std::cout.write(current_chunk, 144) << std::endl;
                    int bytesWrote = write(outfd, current_chunk, 144);
                    currLen = 0;
                    std::cout << "PacketDetector wrote " << bytesWrote << std::endl;
                } else {
                    memmove(current_chunk, current_chunk + 1, 143);
                    current_chunk[143] = bit;
                }
            }
        }
    }

    // inputFile.close();
}


// Test function to ensure code continues to read new bits
// Function to simulate writing bits to the file
// void writeBits(const std::string& filename) {
//     std::ofstream outputFile(filename, std::ios::app); // Open in append mode
//     if (!outputFile) {
//         std::cerr << "Error opening file for writing!" << std::endl;
//         return;
//     }

//     while (running.load()) {
//         // std::this_thread::sleep_for(std::chrono::seconds(2)); // Simulate writing delay
//         std::string randomBits = (rand() % 2 == 0) ? "111111111111111" : "000101111";
//         outputFile << randomBits;
//         outputFile.flush();  // Ensure the data is immediately written
//         // std::cout << "[Writer] Added: " << randomBits << std::endl;
//     }

//     outputFile.close();
// }






int main(int argc, char* argv[]) {

    if (argc != 3)
    {
        std::cout << "Error: PacketDetector.cpp not provided the correct arguments! Require a named pipe input and output (2 args)" << std::endl;
        return 0;
    }

    char *pipe_input = argv[1];
    char *pipe_output = argv[2];

    int input_fd = open(pipe_input, O_RDONLY);
    int output_fd = open(pipe_output, O_WRONLY | O_APPEND);

    if (input_fd == -1 || output_fd == -1)
    {
        perror("Error: bchdecode.cpp failed to open named pipe");
        return 1;
    }

    // Start processing and writing threads
    processStream(input_fd, output_fd);

    // Thread used for testing reading from file
    // std::thread writerThread(writeBits, filename);

    // Wait for user input to stop
    // std::cout << "Press Enter to stop the program..." << std::endl;
    // std::cin.get();
    // running.store(false); // Stop both threads

    // streamThread.join();
    // writerThread.join();

    close(input_fd);
    close(output_fd);

    return 0;
}
