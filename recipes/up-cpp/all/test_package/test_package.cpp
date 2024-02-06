#include <cstdlib>
#include <iostream>

#include <up-cpp/uuid/factory/Uuidv8Factory.h>
#include <up-cpp/uuid/serializer/UuidSerializer.h>

using namespace uprotocol::uuid;
using namespace uprotocol::v1;

int main(void) {
    UUID uuId = Uuidv8Factory::create();
    std::vector<uint8_t> vectUuid = UuidSerializer::serializeToBytes(uuId);
    UUID uuIdFromByteArr = UuidSerializer::deserializeFromBytes(vectUuid);
    std::string uuIdStr = UuidSerializer::serializeToString(uuIdFromByteArr);
    std::cout << "UUID: " << uuIdStr << std::endl;
    return EXIT_SUCCESS;
}
