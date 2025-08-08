#include <iostream>
#include <fcntl.h>    // for open(), O_RDONLY, O_WRONLY
#include <unistd.h>   // for close(), read(), write()
#include "MicroGNextRaphael/code/MessageBitParser.h"

int main(int argc, char* argv[]) {
  if (argc != 3) {
    std::cerr << "Usage: " << argv[0] << " <input> <output>\n";
    return 1;
  }

  int infd = open(argv[1], O_RDONLY);
  int outfd = open(argv[2], O_WRONLY);

  if (infd == -1) {
    std::cerr << "Failed to open FIFO: " << argv[1] << "\n";
    return 1;
  }
  
  if (outfd == -1) {
    std::cerr << "Failed to open FIFO: " << argv[2] << "\n";
    return 1;
  }
  constexpr size_t BUFFER_SIZE = 290; // change later
  char buffer[BUFFER_SIZE] = {0};
  bool success = false;
  
  while (true) {
    success = false;
    sleep(1);
    size_t bytes_read = read(infd, buffer, BUFFER_SIZE);

    if (bytes_read > 0) {
      MessageBitParser parsedMSG(buffer, success);
      if (!success) {
        std::cout << "failed to parse at: " << std::string(buffer) << endl;
      }

      std::ostringstream oss;
      oss << "{"
          << "\"bitSyncPattern\": " << parsedMSG.getBitSyncPattern() << ", "
          << "\"frameSyncPattern\": " << parsedMSG.getFrameSyncPattern() << ", "
          << "\"formatFlag\": " << parsedMSG.getFormatFlag() << ", "
          << "\"protocolFlag\": " << parsedMSG.getProtocolFlag() << ", "
          << "\"countryCode\": " << parsedMSG.getCountryCode() << ", "
          << "\"PC\": " << parsedMSG.getPC() << ", "
          << "\"identificationData\": " << parsedMSG.getIdentificationData() << ", "
          << "\"latitudeDirection\": " << parsedMSG.getLatitudeDirection() << ", "
          << "\"latitudeDegrees\": " << parsedMSG.getLatitudeDegrees() << ", "
          << "\"longtitudeDirection\": " << parsedMSG.getLongitudeDirection() << ", "
          << "\"longtitudeDegrees\": " << parsedMSG.getLongitudeDegrees() << ", "
          << "\"bch1\": " << parsedMSG.getBCH1() << ", "
          << "\"supplementaryData\": " << parsedMSG.getSupplementaryData() << ", "
          << "\"getLatitudeSign\": " << parsedMSG.getLatitudeSign() << ", "
          << "\"getLatitudeMinutes\": " << parsedMSG.getLatitudeMinutes() << ", "
          << "\"getLatitudeSecond\": " << parsedMSG.getLatitudeSeconds() << ", "
          << "\"getLongitudeSign\": " << parsedMSG.getLongitudeSign() << ", "
          << "\"getLongitudeMinutes\": " << parsedMSG.getLongitudeMinutes() << ", "
          << "\"getLongitudeSecond\": " << parsedMSG.getLongitudeSeconds() << ", "
          << "\"bch2\": " << parsedMSG.getBCH2()
          << "}\n";
      std::string json = oss.str();
      int bytesWrote = write(outfd, json.c_str(), json.length());
      std::cout << "logger wrote " << bytesWrote << " bytes to output\n";
    }
  }
  
  return 0;
}