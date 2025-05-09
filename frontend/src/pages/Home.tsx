import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Heading,
  VStack,
  useToast,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Button,
  HStack,
  IconButton,
  useDisclosure,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Spinner,
  Center,
  Fade,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { DeleteIcon } from "@chakra-ui/icons";
import PDFUploader from "../components/PDFUploader";
import { Document } from "../types";

const Home = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingDocuments, setIsFetchingDocuments] = useState(true);
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(
    null
  );
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = React.useRef(null);
  const toast = useToast();
  const navigate = useNavigate();

  const fetchDocuments = async () => {
    setIsFetchingDocuments(true);
    try {
      const response = await fetch("http://localhost:8000/documents/");
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch documents",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsFetchingDocuments(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUploadSuccess = () => {
    fetchDocuments();
    toast({
      title: "Success",
      description: "PDF uploaded successfully",
      status: "success",
      duration: 3000,
      isClosable: true,
    });
  };

  const handleDeleteClick = (document: Document) => {
    setDocumentToDelete(document);
    onOpen();
  };

  const confirmDelete = async () => {
    if (!documentToDelete) return;

    console.log("Attempting to delete document:", documentToDelete);

    setIsLoading(true);

    try {
      console.log(
        `Sending DELETE request to: http://localhost:8000/documents/${documentToDelete.id}`
      );

      const response = await fetch(
        `http://localhost:8000/documents/${documentToDelete.id}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("Delete response status:", response.status);

      if (response.ok) {
        const responseData = await response.json().catch(() => ({}));
        console.log("Delete success response:", responseData);

        // Log database success message from backend
        if (responseData.message) {
          console.log("Server message:", responseData.message);
        }

        toast({
          title: "Success",
          description:
            "Document deleted successfully from database and storage",
          status: "success",
          duration: 3000,
          isClosable: true,
        });

        // Refresh the document list
        await fetchDocuments();
      } else {
        let errorMessage = "Failed to delete document";

        try {
          const errorData = await response.json();
          console.error("Delete error response (JSON):", errorData);
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If not JSON, try text
          const errorText = await response.text();
          console.error("Delete error response (Text):", errorText);
          errorMessage = errorText || errorMessage;
        }

        throw new Error(`Failed to delete document: ${errorMessage}`);
      }
    } catch (error) {
      console.error("Delete operation error:", error);

      toast({
        title: "Database Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to delete document from database",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
      onClose();
      setDocumentToDelete(null);
    }
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={4}>
            Upload PDF
          </Heading>
          <PDFUploader onUploadSuccess={handleUploadSuccess} />
        </Box>

        <Box>
          <Heading size="lg" mb={4}>
            Your Documents
          </Heading>

          {isFetchingDocuments ? (
            <Center py={10}>
              <VStack spacing={4}>
                <Spinner
                  thickness="4px"
                  speed="0.65s"
                  emptyColor="gray.200"
                  color="brand.500"
                  size="xl"
                />
                <Text color="gray.500">Loading documents...</Text>
              </VStack>
            </Center>
          ) : documents.length === 0 ? (
            <Fade in={!isFetchingDocuments}>
              <Text color="gray.500">
                No documents found. Upload a PDF to get started.
              </Text>
            </Fade>
          ) : (
            <Fade in={!isFetchingDocuments}>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                {documents.map((doc) => (
                  <Card key={doc.id} variant="outline">
                    <CardHeader>
                      <HStack justifyContent="space-between">
                        <Text fontWeight="bold">{doc.original_filename}</Text>
                        <IconButton
                          aria-label="Delete document"
                          icon={<DeleteIcon />}
                          colorScheme="red"
                          size="sm"
                          onClick={() => handleDeleteClick(doc)}
                        />
                      </HStack>
                      <Text fontSize="sm" color="gray.500">
                        Uploaded on{" "}
                        {new Date(doc.upload_date).toLocaleDateString()}
                      </Text>
                    </CardHeader>
                    <CardBody>
                      <Button
                        colorScheme="brand"
                        onClick={() => navigate(`/document/${doc.id}`)}
                      >
                        View Document
                      </Button>
                    </CardBody>
                  </Card>
                ))}
              </SimpleGrid>
            </Fade>
          )}
        </Box>
      </VStack>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Document
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete "
              {documentToDelete?.original_filename}"? This action cannot be
              undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button
                colorScheme="red"
                onClick={confirmDelete}
                ml={3}
                isLoading={isLoading}
              >
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Container>
  );
};

export default Home;
