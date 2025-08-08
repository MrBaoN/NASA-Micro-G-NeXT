#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <itpp/itbase.h>
#include <itpp/itcomm.h>
#include "MessageBitParser.h"
#include <fcntl.h>    // for open(), O_RDONLY, O_WRONLY
#include <unistd.h>   // for close(), read(), write()
#include <sys/stat.h> // for mkfifo() if you’re creating the FIFO
#include <cstdint>
#include <cstring>
#include <ctime>
#include <chrono>
#include <iomanip>
#include <zmq.hpp>
#include <string>

using namespace std;

// g++ bchdecode.cpp -o bchdecode -litpp

void superlog(const std::string &message)
{
    std::cout << message << std::endl;
    std::ofstream thisFile("LOGGING.txt", std::ios::app); // Open in append mode
    if (thisFile.is_open()) {
        thisFile << " MESSAGE: " << message << std::endl;
        thisFile.close();
    } else {
        std::cerr << "Failed to open log file!" << std::endl;
    }
}

// Convert a bvec back into a string
std::string bvec_to_string(const itpp::bvec &bits)
{
    string bitString;
    for (int i = 0; i < bits.size(); ++i)
    {
        bitString.push_back(bits[i] ? '1' : '0');
    }

    return bitString;
}

// Used to convert a string into a format itpp::bvec() can handle (just space seperated; Ex: "1 1 1 1 1..." instead of "11111...")
std::string insert_spaces(const std::string &bit_str)
{
    std::string spaced;
    for (size_t i = 0; i < bit_str.size(); ++i)
    {
        spaced += bit_str[i];
        if (i < bit_str.size() - 1)
            spaced += ' ';
    }
    return spaced;
}

uint64_t bitstring_to_uint(const char *bit_array, size_t length)
{
    uint64_t result = 0;

    for (size_t i = 0; i < length; ++i)
    {
        char bit = bit_array[i];

        if (bit == '0')
        {
            result = (result << 1);
        }
        else if (bit == '1')
        {
            result = (result << 1) | 1;
        }
        else
        {
            throw std::invalid_argument("Input contains non-binary character");
        }
    }

    return result;
}

int main(int argc, char *argv[])
{
    superlog("Starting bchdecode.cpp");
    zmq::context_t context(1);
    zmq::socket_t socket(context, zmq::socket_type::pull);
    socket.bind("tcp://*:5556");
    superlog("bchdecode.cpp bound to socket, listening...");

    if (argc != 4)
    {
        std::cout << "Error: bchdecode.cpp not provided the correct arguments! Require a named pipe input and output (2 args)" << std::endl;
        return 0;
    }

    // char *named_pipe_input = argv[1]; // Name of the file to read data from
    char *cast_file = argv[2];        // Name of the file to write data to
    char *kml_file = argv[3];         // Name of the file to write data to
    std::string logOutput = "output.log";

    // Open the files for reading and writing
    // int input_fd = open(named_pipe_input, O_RDONLY);
    int cast_fd = open(cast_file, O_WRONLY | O_APPEND);
    int kml_fd = open(kml_file, O_WRONLY | O_APPEND);
    int log_fd = open(logOutput.c_str(), O_WRONLY | O_APPEND | O_CREAT, 0644);

    if (cast_fd == -1)
    {
        perror("Error: bchdecode.cpp failed to open output pipe");
        return 1;
    }
    if (log_fd == -1)
    {
        perror("Error: bchdecode.cpp failed to open file");
        return 1;
    }

    char readBuf[144];

    while (true)
    {
        // Read data from the zmq tcp client
        zmq::message_t request;
        auto result = socket.recv(request, zmq::recv_flags::none);
        int bytes_read = request.size();
        std::string message = request.to_string();
        superlog("Received message: " + message);


        std::string input;

        if (bytes_read > 0)
        {
            // Get the current system time
            auto now = std::chrono::system_clock::now();
            std::time_t now_time = std::chrono::system_clock::to_time_t(now);

            // Convert to GMT/UTC time structure
            std::tm *gmt = std::gmtime(&now_time);

            // Format the GMT time into a string
            std::ostringstream time;
            time << std::put_time(gmt, "%Y-%m-%d %H:%M:%S");

            std::string gmt_time_str = time.str();
            std::cout << "Current GMT time: " << gmt_time_str << std::endl;

            input = message;
            superlog("Received: " + input);

            std::string spacedInput = insert_spaces(input);

            itpp::bvec bitsVec;
            bitsVec = itpp::bvec(spacedInput);

            superlog("Size of bitsVec: " + std::to_string(bitsVec.size()));

            /* define positions for bit locations */
            int PDF_1_start = 24; // First Protected Data Field (PDF-1) start index
            int BCH_1_start = 85; // index for BCH-1 start
            int BCH_1_end = 105;  // index for BCH-1 end

            /*  BCH::BCH(int in_n, int in_t, bool sys):


                The first protected data field (PDF-1) is 61 bits long, and its associated BCH check bits (BCH-1) are 21 bits,
                giving a total codeword length of n = 61 + 21 = 82.


                However, standard BCH codes require n to be of the form n = 2^m - 1 for some positive integer m.
                Since 2^7 = 128, the smallest valid BCH length that satisfies this condition is n = 127.


                Therefore, we use a (127, k) BCH code and shorten it to fit our (82, 61) structure.


                Additioanlly, t = 3 is the maximum number of bit errors that can be corrected. With this specific constructor (as
                opposed to "BCH::BCH(int in_n, int in_k, int in_t, const ivec &genpolynom, bool sys)"), we specify how many bits we want to be able
                to correct, and the constructor deduces the polynomial generator to use with that given 't'.


                Lastly, since we are given an encoded message, we are not to concerened about what the generator polynomial is.
                This is because the generator polynomial is not used directly in decoding; However, it does define the strucutre of our BCH code.


                sys = false -> Signifying the BCH code will be strucuted like -> | [bch_bits | message_bits] |
            */
            itpp::BCH bchCode1(127, 3, true);

            // Grab parts of full bitVec for decodng
            itpp::bvec BCH_1_bits = bitsVec.get(BCH_1_start, BCH_1_end);       // 21 bits
            itpp::bvec PDF_1_bits = bitsVec.get(PDF_1_start, BCH_1_start - 1); // 61 bits
            itpp::bvec n_bit_message_1 = concat(PDF_1_bits, BCH_1_bits);       // 82 bits

            itpp::bvec PDF_1_decoded_with_padding; // Where the decoded message will be stored
            itpp::bvec firstFailBitsVec;           // Stores validity of each block

            itpp::bvec padded_codeword_1 = concat(itpp::zeros_b(127 - n_bit_message_1.size()), n_bit_message_1);

            /* decode and hope it works */
            bool PDF1_success = bchCode1.decode(padded_codeword_1, PDF_1_decoded_with_padding, firstFailBitsVec);

            itpp::bvec decoded_PDF1 = PDF_1_decoded_with_padding.get(PDF_1_decoded_with_padding.size() - 82 + 21, PDF_1_decoded_with_padding.size() - 1);

            /* See if decoding suceeded */
            std::cout << "\n=== [BCH-1 DECODING RESULTS] ===\n";
            std::cout << "Raw Codeword (BCH|PDF):\n"
                      << padded_codeword_1 << std::endl;
            std::cout << "Decoded PDF with some padding still:\n"
                      << PDF_1_decoded_with_padding << std::endl;
            std::cout << "PDF size: " << PDF_1_decoded_with_padding.size() << endl;
            std::cout << "Decode success: " << (PDF1_success ? "✅ Yes" : "❌ No") << std::endl;
            std::cout << "Validity flags: " << firstFailBitsVec << std::endl;
            std::cout << "finalPDF:\n"
                      << decoded_PDF1 << std::endl;
            std::cout << "decoded_PDF1 size: " << decoded_PDF1.size() << std::endl;
            std::cout << "===============================\n\n";

            //!-----------------------------------------------Seperator-----------------------------------------------!//

            // Define positions for bit locations
            int PDF_2_start = 106; // Second Protected Data Field (PDF-2) start index
            int BCH_2_start = 132; // BCH-2 start index
            int BCH_2_end = 143;   // BCH-2 end index

            // Initialize BCH decoder for BCH-2 (26 data bits + 12 parity bits = 38 total)
            // We use a (63, k) BCH code and shorten it to (38, 26) with t = 2
            itpp::BCH bchCode2(63, 2, true);

            // Grab parts of the full bit vector for decoding
            itpp::bvec BCH_2_bits = bitsVec.get(BCH_2_start, BCH_2_end);       // 12 bits
            itpp::bvec PDF_2_bits = bitsVec.get(PDF_2_start, BCH_2_start - 1); // 26 bits
            itpp::bvec n_bit_message_2 = concat(PDF_2_bits, BCH_2_bits);       // 38 bits [PDF | BCH]

            // Pad with zeros to match expected length (63)
            itpp::bvec padded_codeword_2 = concat(itpp::zeros_b(63 - n_bit_message_2.size()), n_bit_message_2);

            itpp::bvec PDF_2_decoded_with_padding; // Where the decoded message will be stored
            itpp::bvec secondFailBitsVec;          // Stores validity of each block

            // Decode and hope it works
            bool PDF2_success = bchCode2.decode(padded_codeword_2, PDF_2_decoded_with_padding, secondFailBitsVec);

            itpp::bvec decoded_PDF2 = PDF_2_decoded_with_padding.get(PDF_2_decoded_with_padding.size() - 38 + 12, PDF_2_decoded_with_padding.size() - 1);

            std::cout << "\n=== [BCH-2 DECODING RESULTS] ===\n";
            std::cout << "Raw Codeword (PDF|BCH):\n"
                      << padded_codeword_2 << std::endl;
            std::cout << "Decoded PDF with some padding still:\n"
                      << PDF_2_decoded_with_padding << std::endl;
            std::cout << "PDF size: " << PDF_2_decoded_with_padding.size() << std::endl;
            std::cout << "decoded_PDF2:\n"
                      << decoded_PDF2 << std::endl;
            std::cout << "decoded_PDF2 size: " << decoded_PDF2.size() << std::endl;
            std::cout << "Decode success: " << (PDF2_success ? "✅ Yes" : "❌ No") << std::endl;
            std::cout << "Validity flags: " << secondFailBitsVec << std::endl;
            std::cout << "===============================\n\n";

            //!-----------------------------------------------Seperator-----------------------------------------------!//

            // Convert he original non decoded message to a string to send to FIFO
            string original_bytes = bvec_to_string(bitsVec);

            std::cout << "Original Bytes:\n"
                      << original_bytes << " -> size: " << original_bytes.size() << endl
                      << endl;

            // Concatinate the full 144 bit message
            itpp::bvec decoded_144_bvec;
            decoded_144_bvec = concat(
                concat(
                    concat(
                        concat(
                            bitsVec.get(0, 24 - 1), // Bit Sync and Fram Sync (bits 1 - 24)
                            decoded_PDF1            // Decoded PDF-1 (61 bits)
                            ),
                        BCH_1_bits // BCH-1 (21 bits)
                        ),
                    decoded_PDF2 // Decoded PDF-2 (26 bits)
                    ),
                BCH_2_bits // BCH-2 (12 bits)
            );

            // Convert the full 144 bit decoded bvec to a string to be sent to the FIFO
            string decoded_bits = bvec_to_string(decoded_144_bvec);

            cout << "Decoded Bytes:\n"
                 << decoded_bits << " -> size: " << decoded_bits.size() << endl
                 << endl;

            MessageBitParser parsedMSG(original_bytes, decoded_bits, PDF1_success, PDF2_success); // Call MessageBitParser
            std::ostringstream oss;
            oss << "{"
                << "\"bitSyncPattern\": \"" << parsedMSG.getBitSyncPattern() << "\", "
                << "\"frameSyncPattern\": \"" << parsedMSG.getFrameSyncPattern() << "\", "
                << "\"formatFlag\": \"" << parsedMSG.getFormatFlag() << "\", "
                << "\"protocolFlag\": \"" << parsedMSG.getProtocolFlag() << "\", "
                << "\"countryCode\": \"" << parsedMSG.getCountryCode() << "\", "
                << "\"PC\": \"" << parsedMSG.getPC() << "\", "
                << "\"identificationData\": \"" << parsedMSG.getIdentificationData() << "\", "
                << "\"parsedIdentData\": \"" << parsedMSG.getParsedIdentificationData() << "\", "
                << "\"bch1\": \"" << parsedMSG.getBCH1() << "\", "
                << "\"bch1Succ\": \"" << parsedMSG.getBCH1Success() << "\", "
                << "\"supplementaryData\": \"" << parsedMSG.getSupplementaryData() << "\", "
                << "\"bch2\": \"" << parsedMSG.getBCH2() << "\", "
                << "\"bch2Succ\": \"" << parsedMSG.getBCH2Success() << "\", "
                << "\"N_or_S\": \"" << parsedMSG.getLatitudeDirection() << "\", "
                << "\"finalLat\": \"" << parsedMSG.getFinalLat() << "\", "
                << "\"E_or_W\": \"" << parsedMSG.getLongitudeDirection() << "\", "
                << "\"finalLong\": \"" << parsedMSG.getFinalLon() << "\", "
                << "\"beconHexID\": \"" << parsedMSG.getBeaconHexID() << "\", "
                << "\"Time\": \"" << gmt_time_str << "\" "
                << "}" << std::endl;
            std::string json = oss.str();
            std::ostringstream log_oss;

            

            log_oss << "{"
                    << "\"Original\": \"" << parsedMSG.getOriginalMsg() << "\", "
                    << "\"Decoded\": \"" << parsedMSG.getDecodedMsg() << "\", "
                    << "\"bitSyncPattern\": \"" << parsedMSG.getBitSyncPattern() << "\", "
                    << "\"frameSyncPattern\": \"" << parsedMSG.getFrameSyncPattern() << "\", "
                    << "\"formatFlag\": \"" << parsedMSG.getFormatFlag() << "\", "
                    << "\"protocolFlag\": \"" << parsedMSG.getProtocolFlag() << "\", "
                    << "\"countryCode\": \"" << parsedMSG.getCountryCode() << "\", "
                    << "\"PC\": \"" << parsedMSG.getPC() << "\", "
                    << "\"identificationData\": \"" << parsedMSG.getIdentificationData() << "\", "
                    << "\"parsedIdentData\": \"" << parsedMSG.getParsedIdentificationData() << "\", "
                    << "\"bch1\": \"" << parsedMSG.getBCH1() << "\", "
                    << "\"bch1Succ\": \"" << parsedMSG.getBCH1Success() << "\", "
                    << "\"supplementaryData\": \"" << parsedMSG.getSupplementaryData() << "\", "
                    << "\"bch2\": \"" << parsedMSG.getBCH2() << "\", "
                    << "\"bch2Succ\": \"" << parsedMSG.getBCH2Success() << "\", "
                    << "\"N_or_S\": \"" << parsedMSG.getLatitudeDirection() << "\", "
                    << "\"finalLat\": \"" << parsedMSG.getFinalLat() << "\", "
                    << "\"E_or_W\": \"" << parsedMSG.getLongitudeDirection() << "\", "
                    << "\"finalLong\": \"" << parsedMSG.getFinalLon() << "\", "
                    << "\"beconHexID\": \"" << parsedMSG.getBeaconHexID() << "\", "
                    << "\"Time\": \"" << gmt_time_str << "\" "
                    << "}" << std::endl;
            std::string log_json = log_oss.str();

            superlog("Parsed JSON: " + json);

            int bytesWrote = write(cast_fd, json.c_str(), json.length());
            std::cout << "bch wrote " << bytesWrote << " to caster" << std::endl;
            bytesWrote = write(kml_fd, json.c_str(), json.length());
            std::cout << "bch wrote " << bytesWrote << " to kml" << std::endl;
            bytesWrote = write(log_fd, log_json.c_str(), log_json.length());
            std::cout << "bch wrote " << bytesWrote << " to log file" << std::endl;

            superlog("Wrote to files: " + std::to_string(bytesWrote) + " bytes");

        }

        
        // After processing each message and writing to files, send tcp response
        // zmq::message_t reply(5);
        // memcpy(reply.data(), "Done", 5);
        // socket.send(reply, zmq::send_flags::none);
    }

    // close(input_fd);
    close(cast_fd);
    close(kml_fd);
    close(log_fd);
    return 0;
}
