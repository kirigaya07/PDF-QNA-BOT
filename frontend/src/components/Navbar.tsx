import React from "react";
import { Box, Flex, Heading } from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";

const Navbar = () => {
  return (
    <Box bg="white" px={4} shadow="sm">
      <Flex h={16} alignItems="center" justifyContent="space-between">
        <Heading as={RouterLink} to="/" size="md" color="brand.500">
          PDF Q&A
        </Heading>
      </Flex>
    </Box>
  );
};

export default Navbar;
