#ifndef MESSAGEBITPARSER_H
#define MESSAGEBITPARSER_H

#include <iostream>
#include <itpp/itbase.h>
#include <itpp/itcomm.h>
#include <vector>
#include <string>
#include <iomanip>
#include <unordered_map>
#include <bitset>
#include <sstream>

using namespace std;

std::unordered_map<int, std::string> country_codes = {
    {201, "ALBANIA"},
    {202, "ANDORRA"},
    {203, "AUSTRIA"},
    {204, "AZORES-POR"},
    {205, "BELGIUM"},
    {206, "BELARUS"},
    {207, "BULGARIA"},
    {208, "VATICAN"},
    {209, "CYPRUS"},
    {210, "CYPRUS"},
    {211, "GERMANY"},
    {212, "CYPRUS"},
    {213, "GEORGIA"},
    {214, "MOLDOVA"},
    {215, "MALTA"},
    {216, "ARMENIA"},
    {218, "GERMANY"},
    {219, "DENMARK"},
    {220, "DENMARK"},
    {224, "SPAIN"},
    {225, "SPAIN"},
    {226, "FRANCE"},
    {227, "FRANCE"},
    {228, "FRANCE"},
    {229, "MALTA"},
    {230, "FINLAND"},
    {231, "FAROE ISLANDS-DK"},
    {232, "UNITED KINGDOM"},
    {233, "UNITED KINGDOM"},
    {234, "UNITED KINGDOM"},
    {235, "UNITED KINGDOM"},
    {236, "GIBRALTAR-UK"},
    {237, "GREECE"},
    {238, "CROATIA"},
    {239, "GREECE"},
    {240, "GREECE"},
    {241, "GREECE"},
    {242, "MOROCCO"},
    {243, "HUNGARY"},
    {244, "NETHERLANDS"},
    {245, "NETHERLANDS"},
    {246, "NETHERLANDS"},
    {247, "ITALY"},
    {248, "MALTA"},
    {249, "MALTA"},
    {250, "IRELAND"},
    {251, "ICELAND"},
    {252, "LIECHTENSTEIN"},
    {253, "LUXEMBOURG"},
    {254, "MONACO"},
    {255, "MADEIRA-POR"},
    {256, "MALTA"},
    {257, "NORWAY"},
    {258, "NORWAY"},
    {259, "NORWAY"},
    {261, "POLAND"},
    {262, "MONTENEGRO"},
    {263, "PORTUGAL"},
    {264, "ROMANIA"},
    {265, "SWEDEN"},
    {266, "SWEDEN"},
    {267, "SLOVAKIA"},
    {268, "SAN MARINO"},
    {269, "SWITZERLAND"},
    {270, "CZECH REPUBLIC"},
    {271, "TÜRKIYE"},
    {272, "UKRAINE"},
    {273, "RUSSIAN FEDERAT"},
    {274, "NORTH MACEDONIA"},
    {275, "LATVIA"},
    {276, "ESTONIA"},
    {277, "LITHUANIA"},
    {278, "SLOVENIA"},
    {279, "SERBIA"},
    {301, "ANGUILLA-UK"},
    {303, "ALASKA-USA"},
    {304, "ANTIGUA & BARBUD"},
    {305, "ANTIGUA & BARBUD"},
    {306, "NETH ANTILLES-NL"},
    {307, "ARUBA-NL"},
    {308, "BAHAMAS"},
    {309, "BAHAMAS"},
    {310, "BERMUDA-UK"},
    {311, "BAHAMAS"},
    {312, "BELIZE"},
    {314, "BARBADOS"},
    {316, "CANADA"},
    {319, "CAYMAN ISL-UK"},
    {321, "COSTA RICA"},
    {323, "CUBA"},
    {325, "DOMINICA"},
    {327, "DOMINICAN REP"},
    {329, "GUADELOUPE-FR"},
    {330, "GRENADA"},
    {331, "GREENLAND-DK"},
    {332, "GUATEMALA"},
    {334, "HONDURAS"},
    {336, "HAITI"},
    {338, "USA"},
    {339, "JAMAICA"},
    {341, "ST KITTS & NEVIS"},
    {343, "ST LUCIA"},
    {345, "MEXICO"},
    {347, "MARTINIQUE-FR"},
    {348, "MONTSERRAT"},
    {350, "NICARAGUA"},
    {351, "PANAMA"},
    {352, "PANAMA"},
    {353, "PANAMA"},
    {354, "PANAMA"},
    {355, "PANAMA"},
    {356, "PANAMA"},
    {357, "PANAMA"},
    {358, "PUERTO RICO-USA"},
    {359, "EL SALVADOR"},
    {361, "ST PIERRE MIQ-FR"},
    {362, "TRINIDAD TOBAGO"},
    {364, "TURKS CAICOS-UK"},
    {366, "USA"},
    {367, "USA"},
    {368, "USA"},
    {369, "USA"},
    {370, "PANAMA"},
    {371, "PANAMA"},
    {372, "PANAMA"},
    {373, "PANAMA"},
    {374, "PANAMA"},
    {375, "ST VINCENT & GRE"},
    {376, "ST VINCENT & GRE"},
    {377, "ST VINCENT & GRE"},
    {378, "BRI VIRGIN IS-UK"},
    {379, "US VIRGIN IS-USA"},
    {401, "AFGHANISTAN"},
    {403, "SAUDI ARABIA"},
    {405, "BANGLADESH"},
    {408, "BAHRAIN"},
    {410, "BHUTAN"},
    {412, "CHINA"},
    {413, "CHINA"},
    {414, "CHINA"},
    {416, "ITDC (TAIWAN)"},
    {417, "SRI LANKA"},
    {419, "INDIA"},
    {422, "IRAN"},
    {423, "AZERBAIJAN"},
    {425, "IRAQ"},
    {428, "ISRAEL"},
    {431, "JAPAN"},
    {432, "JAPAN"},
    {434, "TURKMENISTAN"},
    {436, "KAZAKHSTAN"},
    {437, "UZBEKISTAN"},
    {438, "JORDAN"},
    {440, "KOREA (REP OF)"},
    {441, "KOREA (REP OF)"},
    {443, "PALESTINE AUTH"},
    {445, "DEM PEO RP KOREA"},
    {447, "KUWAIT"},
    {450, "LEBANON"},
    {451, "KYRGYZ REPUBLIC"},
    {453, "MACAO-CHN"},
    {455, "MALDIVES"},
    {457, "MONGOLIA"},
    {459, "NEPAL"},
    {461, "OMAN"},
    {463, "PAKISTAN"},
    {466, "QATAR"},
    {468, "SYRIA"},
    {470, "UNITED ARAB EMIR"},
    {471, "UNITED ARAB EMIR"},
    {472, "TAJIKISTAN"},
    {473, "YEMEN"},
    {475, "YEMEN"},
    {477, "HONG KONG-CHN"},
    {478, "BOSNIA & HERZEGO"},
    {501, "ADELIE LAND-FR"},
    {503, "AUSTRALIA"},
    {506, "MYANMAR"},
    {508, "BRUNEI"},
    {510, "MICRONESIA"},
    {511, "PALAU"},
    {512, "NEW ZEALAND"},
    {514, "CAMBODIA"},
    {515, "CAMBODIA"},
    {516, "CHRISTMAS IS-AUS"},
    {518, "COOK ISLANDS-NZ"},
    {520, "FIJI"},
    {523, "COCOS ISL-AUS"},
    {525, "INDONESIA"},
    {529, "KIRIBATI"},
    {531, "LAOS"},
    {533, "MALAYSIA"},
    {536, "NO MARIAN IS-USA"},
    {538, "MARSHALL ISLANDS"},
    {540, "NEW CALEDONIA-FR"},
    {542, "NIUE ISLAND-NZ"},
    {544, "NAURU"},
    {546, "FRENCH POLYNE-FR"},
    {548, "PHILIPPINES"},
    {550, "TIMOR LESTE"},
    {553, "PAPUA NEW GUINEA"},
    {555, "PITCAIRN ISL-UK"},
    {557, "SOLOMON ISLANDS"},
    {559, "AMERIC SAMOA-USA"},
    {561, "SAMOA (IND.STAT)"},
    {563, "SINGAPORE"},
    {564, "SINGAPORE"},
    {565, "SINGAPORE"},
    {566, "SINGAPORE"},
    {567, "THAILAND"},
    {570, "TONGA"},
    {572, "TUVALU"},
    {574, "VIET NAM"},
    {576, "VANUATU"},
    {577, "VANUATU"},
    {578, "WALLIS FUTUNA-FR"},
    {601, "SOUTH AFRICA"},
    {603, "ANGOLA"},
    {605, "ALGERIA"},
    {607, "ST PAUL AMSTE-FR"},
    {608, "ASCENSION ISL-UK"},
    {609, "BURUNDI"},
    {610, "BENIN"},
    {611, "BOTSWANA"},
    {612, "CENTRAL AFRI REP"},
    {613, "CAMEROON"},
    {615, "CONGO (REP OF)"},
    {616, "COMOROS"},
    {617, "CABO VERDE"},
    {618, "CROZET ARCHIP-FR"},
    {619, "IVORY COAST"},
    {620, "COMOROS"},
    {621, "DJIBOUTI"},
    {622, "EGYPT"},
    {624, "ETHIOPIA"},
    {625, "ERITREA"},
    {626, "GABON"},
    {627, "GHANA"},
    {629, "GAMBIA"},
    {630, "GUINEA-BISSAU"},
    {631, "EQUAT GUINEA"},
    {632, "GUINEA"},
    {633, "BURKINA FASO"},
    {634, "KENYA"},
    {635, "KERGUELEN IS-FR"},
    {636, "LIBERIA"},
    {637, "LIBERIA"},
    {638, "SOUTH SUDAN"},
    {642, "LIBYA"},
    {644, "LESOTHO"},
    {645, "MAURITIUS"},
    {647, "MADAGASCAR"},
    {649, "MALI"},
    {650, "MOZAMBIQUE"},
    {654, "MAURITANIA"},
    {655, "MALAWI"},
    {656, "NIGER"},
    {657, "NIGERIA"},
    {659, "NAMIBIA"},
    {660, "REUNION MAYOT-FR"},
    {661, "RWANDA"},
    {662, "SUDAN"},
    {663, "SENEGAL"},
    {664, "SEYCHELLES"},
    {665, "ST HELENA-UK"},
    {666, "SOMALIA"},
    {667, "SIERRA LEONE"},
    {668, "SAO TOME & PRINC"},
    {669, "ESWATINI"},
    {670, "CHAD"},
    {671, "TOGO"},
    {672, "TUNISIA"},
    {674, "TANZANIA"},
    {675, "UGANDA"},
    {676, "DEM REP CONGO"},
    {677, "TANZANIA"},
    {678, "ZAMBIA"},
    {679, "ZIMBABWE"},
    {701, "ARGENTINA"},
    {710, "BRAZIL"},
    {720, "BOLIVIA"},
    {725, "CHILE"},
    {730, "COLOMBIA"},
    {735, "ECUADOR"},
    {740, "FALKLAND ISL-UK"},
    {745, "GUIANA FRENCH-FR"},
    {750, "GUYANA"},
    {755, "PARAGUAY"},
    {760, "PERU"},
    {765, "SURINAME"},
    {770, "URUGUAY"},
    {775, "VENEZUELA"},
    {974, "miscoded"},
    {982, "miscoded"},
    {983, "miscoded"},
    {984, "miscoded"},
    {985, "miscoded"},
    {986, "miscoded"},
    {987, "miscoded"},
};

class MessageBitParser
{
public:
    // Full Original and Decoded
    std::string getOriginalMsg() const { return nonDecodedMSG; }
    std::string getDecodedMsg() const { return decodedMsg; }

    // Bit Sync and Frame Sync
    std::string getBitSyncPattern() const { return bit_sync_pattern; }
    std::string getFrameSyncPattern() const { return frame_sync_pattern; }

    // Format and Protocol Information
    std::string getFormatFlag() const { return format_flag; }
    std::string getProtocolFlag() const { return protocol_flag; }
    std::string getCountryCode() const { return country_code; }

    // Beacon Hex ID (bits 26-85 turned into Hex)
    std::string getBeaconHexID() const { return beacon_hex_id; }

    // PDF-1: Identification & Location
    std::string getPC() const { return PC; }
    std::string getIdentificationData() const { return identification_data; }

    // PDF-1: Latitude and Longitude
    std::string getLatitudeDirection() const { return N_or_S; }  // N = 0, S = 1
    std::string getLongitudeDirection() const { return E_or_W; } // E = 0, W = 1

    // BCH-1 (Error Correction for PDF-1)
    std::string getBCH1() const { return BCH_1; }

    // PDF-2: Supplementary Data
    std::string getSupplementaryData() const { return supp_data; }

    std::string getFinalLat() const { return final_lat; }
    std::string getFinalLon() const { return final_lon; }

    // BCH-2 (Error Correction for PDF-2)
    std::string getBCH2() const { return BCH_2; }

    std::string getBCH1Success() const { return BCH_1_Success; }
    std::string getBCH2Success() const { return BCH_2_Success; }
    std::string getParsedIdentificationData() const { return parsed_identification_data; }

    MessageBitParser(std::string original, std::string decoded, bool BCH1_success, bool BCH2_success)
    {
        nonDecodedMSG = original; // Start at index 0 and grab the next 144 characters

        std::cout
            << "nonDecodedMsg:\n"
            << nonDecodedMSG << " -> size = " << nonDecodedMSG.size() << std::endl
            << std::endl;

        decodedMsg = decoded; // Start at index 0 and grab the next 144 characters

        std::cout << "decoded Msg:\n"
                  << decodedMsg << " -> size = " << decodedMsg.size() << std::endl
                  << std::endl;

        BCH_1_Success = (BCH1_success) ? "yes" : "no";
        std::cout << "BCH_1_Success: " << BCH_1_Success << std::endl;
        BCH_2_Success = (BCH2_success) ? "yes" : "no";
        std::cout << "BCH_2_Success: " << BCH_2_Success << std::endl;

        bit_sync_pattern = decodedMsg.substr(0, 15);   // Bits 1-15 (15 bits)
        frame_sync_pattern = decodedMsg.substr(15, 9); // Bits 16-24 (9 bits)

        // Basic Flags
        format_flag = decodedMsg[24];   // Bit 25
        protocol_flag = decodedMsg[25]; // Bit 26

        int code = std::stoi(decodedMsg.substr(26, 10), nullptr, 2);
        country_code = country_codes.count(code) ? country_codes.at(code) : "Unidentifiable Country Code"; // bits 27-36 (10 bits)

        // PDF-1 (Bits 37-85) -> Identification and Location
        PC = decodedMsg.substr(36, 4);                   // Bits 37-40 (4 bits)
        identification_data = decodedMsg.substr(40, 24); // Bits 41-64 (24 bits)
        parsed_identification_data = getParsedIdentificationInfo(identification_data);

        std::string beaconHex = decodedMsg.substr(25, 60); // bits 26-85 (60 bits)
        beacon_hex_id = binaryToHex(beaconHex);            // Convert the bits to HEX

        // TODO If BCH2 decoding fails or is not present, should simply return the value returned from first lat and long
        //! Determine Lat and Long
        // Coarse fields (from PDF-1)

        char lat_dir_bit = decodedMsg[64];                   // Bit 65
        std::string lat_deg_bits = decodedMsg.substr(65, 9); // Bits 66–74

        char lon_dir_bit = decodedMsg[74];                    // Bit 75
        std::string lon_deg_bits = decodedMsg.substr(75, 10); // Bits 76–85

        // // Use coarse bits for N/S and E/W
        // N_or_S = (lat_dir_bit == '0') ? "North" : "South";
        // E_or_W = (lon_dir_bit == '0') ? "East" : "West";

        // // Fine delta fields (from PDF-2)
        // N_or_S = (decodedMsg[112] == '0') ? "North" : "South";                    // Bit 113
        // int delta_lat_min = std::stoi(decodedMsg.substr(113, 5), nullptr, 2);     // Bits 114–118
        // int delta_lat_sec = std::stoi(decodedMsg.substr(118, 4), nullptr, 2) * 4; // Bits 119–122

        // E_or_W = (decodedMsg[122] == '0') ? "East" : "West";                      // Bit 123
        // int delta_lon_min = std::stoi(decodedMsg.substr(123, 5), nullptr, 2);     // Bits 124–128
        // int delta_lon_sec = std::stoi(decodedMsg.substr(128, 4), nullptr, 2) * 4; // Bits 129–132

        // Fine delta fields (from PDF-2) INVETED
        N_or_S = (decodedMsg[112] == '0') ? "South" : "North";                    // Bit 113
        int delta_lat_min = std::stoi(decodedMsg.substr(113, 5), nullptr, 2);     // Bits 114–118
        int delta_lat_sec = std::stoi(decodedMsg.substr(118, 4), nullptr, 2) * 4; // Bits 119–122

        E_or_W = (decodedMsg[122] == '0') ? "West" : "East";                      // Bit 123
        int delta_lon_min = std::stoi(decodedMsg.substr(123, 5), nullptr, 2);     // Bits 124–128
        int delta_lon_sec = std::stoi(decodedMsg.substr(128, 4), nullptr, 2) * 4; // Bits 129–132

        // Convert coarse bits to degrees
        int lat_deg_raw = std::stoi(lat_deg_bits, nullptr, 2);
        int lon_deg_raw = std::stoi(lon_deg_bits, nullptr, 2);

        // Scale them
        double lat_main_deg = lat_deg_raw * 0.25;
        double lon_main_deg = lon_deg_raw * 0.25;

        // Delta values
        double lat_delta_deg = (delta_lat_min + delta_lat_sec / 60.0) / 60.0;
        double lon_delta_deg = (delta_lon_min + delta_lon_sec / 60.0) / 60.0;

        // Combine coarse + fine
        double full_lat = lat_main_deg + lat_delta_deg;
        double full_lon = lon_main_deg + lon_delta_deg;

        // Adjust for N/S and E/W
        if (N_or_S == "South")
        {
            full_lat = -full_lat;
        }
        if (E_or_W == "West")
        {
            full_lon = -full_lon;
        }

        // Format as strings
        std::ostringstream oss_lat, oss_lon;
        oss_lat << std::fixed << std::setprecision(6) << full_lat;
        oss_lon << std::fixed << std::setprecision(6) << full_lon;

        final_lat = oss_lat.str();
        final_lon = oss_lon.str();

        // BCH-1 (Error Correction for PDF-1)
        BCH_1 = decodedMsg.substr(85, 21); // Bits 86-106 (21 bits)

        // PDF-2 (Bits 107-132)-> Supplementary Data
        supp_data = decodedMsg.substr(106, 6); // Bits 107-112 (6 bits)

        // BCH-2 (Error Correction for PDF-2)
        BCH_2 = decodedMsg.substr(132, 12); // Bits 133-144 (12 bits)
    }

private:
    std::string nonDecodedMSG; // The full 144 bits of the original, non-decoded msg
    std::string decodedMsg;    // The full 144 bit decoded msg
    std::string BCH_1_Success; // Represents if the decoding for BCH_1 and PDF_1 succeeded
    std::string BCH_2_Success; // Represents if the decoding for BCH_2 and PDF_2 succeeded

    std::string bit_sync_pattern;   // bits 1-15 (15 bits)
    std::string frame_sync_pattern; // bits 16-24 (9 bits)

    std::string format_flag;   // bit 25
    std::string protocol_flag; // bit 26

    std::string country_code; // bits 27-36 (10 bits)

    std::string beacon_hex_id; // bits 26-85

    /*PDF-1 (bits 37-85)*/
    /*PDF-1 PC and Identification data to determine MMSI, Aircraft,
    Aviation Protocol (Operator Designator & Serial), Test Code / Serial Protocol,
    or Maritime Protocol (Fixed MMSI)*/
    std::string PC;                         // bits 37-40 (4 bits)
    std::string identification_data;        // bits 41-64 (24 bits)
    std::string parsed_identification_data; // bits vary, gets sent as a detailed string

    /*PDF-1 Lat and Long*/
    std::string N_or_S; // bit 65 (1 bit)
    // std::string lat_deg; // bits 66-74 (9 bits)
    std::string E_or_W; // bit 75 (1 bit)
    // std::string lon_deg; // bit 76-85 (10 bits)

    std::string BCH_1;

    /* PDF-2 (bits 107-132)
    /*PDF-2 supplemental data*/
    std::string supp_data; // bits 107-112 (6 bits)

    std::string final_lat;
    std::string final_lon;

    std::string BCH_2;

    // Convert binary string to hex string
    std::string binaryToHex(const std::string &binary)
    {
        // Convert binary string to unsigned long long
        std::bitset<60> bits(binary); // Exactly 60 bits
        unsigned long long value = bits.to_ullong();

        // Now format as hex
        std::stringstream ss;
        ss << std::uppercase << std::hex << value; // uppercase hex, no 0x prefix
        return ss.str();
    }

    // TODO: Make the parsing more descriptive. Download datasets for mapping, etc.
    //  Helper function for getParsedIdentificationInfo to reduce redundancy
    std::string formatCSTA(const std::string &label, const std::string &data)
    {
        int cs_ta_no = std::stoi(data.substr(0, 10), nullptr, 2);   // 10 bits
        int serial_no = std::stoi(data.substr(10, 14), nullptr, 2); // 14 bits

        return label + ": C/S TA No: " + std::to_string(cs_ta_no) +
               ", Serial No: " + std::to_string(serial_no);
    }

    // Used to obtain a detailed string for the identification data
    std::string getParsedIdentificationInfo(const std::string &identification_data)
    {
        if (PC == "0010") // Maritime MMSI + B.No
        {
            int mmsi = std::stoi(identification_data.substr(0, 20), nullptr, 2); // 20 bits
            int b_no = std::stoi(identification_data.substr(20, 4), nullptr, 2); // 4 bits

            return "MMSI: " + std::to_string(mmsi) + ", B.No: " + std::to_string(b_no);
        }
        else if (PC == "0011") // Aircraft 24-bit Address
        {
            int aircraft_address = std::stoi(identification_data, nullptr, 2); // 24 bits

            // Make HEX
            std::stringstream ss;
            ss << std::hex << aircraft_address;

            return "Aircraft 24-bit Address: 0x" + ss.str();
        }
        else if (PC == "0101") // Aircraft Operator Designator + Serial No
        {
            int operator_code = std::stoi(identification_data.substr(0, 15), nullptr, 2); // 15 bits
            int serial_no = std::stoi(identification_data.substr(15, 9), nullptr, 2);     // 9 bits

            return "Aircraft Operator Designator: " + std::to_string(operator_code) +
                   ", Serial No: " + std::to_string(serial_no);
        }
        else if (PC == "0100") // ELT-Serial
        {
            return formatCSTA("ELT-Serial", identification_data);
        }
        else if (PC == "0110") // EPIRB-Serial
        {
            return formatCSTA("EPIRB-Serial", identification_data);
        }
        else if (PC == "0111") // PLB
        {
            return formatCSTA("PLB", identification_data);
        }
        else if (PC == "1100") // Fixed MMSI
        {
            int mmsi_last6 = std::stoi(identification_data.substr(0, 20), nullptr, 2); // 20 bits
            int fixed = std::stoi(identification_data.substr(20, 4), nullptr, 2);      // 4 bits

            // Format MMSI last 6 digits
            std::ostringstream oss;
            oss << std::setw(6) << std::setfill('0') << mmsi_last6;

            return "MMSI (last 6 digits): " + oss.str() + ", Fixed: " + std::to_string(fixed);
        }

        return "Unrecognized PC: Raw Data = " + identification_data;
    }

    void printParsedMessage(MessageBitParser parsedMSG)
    {
        std::cout << "bit_sync_pattern:       " << bit_sync_pattern << " -> size: " << bit_sync_pattern.size() << std::endl;
        std::cout << "frame_sync_pattern:     " << frame_sync_pattern << " -> size: " << frame_sync_pattern.size() << std::endl;

        std::cout << "format_flag:            " << format_flag << " -> size: " << format_flag.size() << std::endl;
        std::cout << "protocol_flag:          " << protocol_flag << " -> size: " << protocol_flag.size() << std::endl;
        std::cout << "country_code:           " << country_code << " -> size: " << country_code.size() << std::endl;

        std::cout << "PC:                     " << PC << " -> size: " << PC.size() << std::endl;
        std::cout << "identification_data:    " << identification_data << " -> size: " << identification_data.size() << std::endl;
        std::cout << "parsed_ident_data:      " << parsed_identification_data << " -> size: " << parsed_identification_data.size() << std::endl;

        std::cout << "N_or_S:                 " << N_or_S << " -> size: " << N_or_S.size() << std::endl;
        std::cout << "FinalLat:               " << final_lat << std::endl;
        std::cout << "E_or_W:                 " << E_or_W << " -> size: " << E_or_W.size() << std::endl;
        std::cout << "FinalLong:              " << final_lon << std::endl;

        std::cout << "BCH_1:                  " << BCH_1 << " -> size: " << BCH_1.size() << std::endl;

        std::cout << "supp_data:              " << supp_data << " -> size: " << supp_data.size() << std::endl;

        std::cout << "BCH_2:                  " << BCH_2 << " -> size: " << BCH_2.size() << std::endl;

        std::cout << "Bit parsing succeeded!" << std::endl;
    }
};

#endif // MESSAGEBITPARSER_H
