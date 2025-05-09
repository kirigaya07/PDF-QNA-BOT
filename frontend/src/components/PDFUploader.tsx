import React, { useCallback, useState } from "react";
import {
  Box,
  Button,
  useToast,
  Text,
  VStack,
  Progress,
} from "@chakra-ui/react";
import { useDropzone } from "react-dropzone";

interface PDFUploaderProps {
  onUploadSuccess: () => void;
}

const PDFUploader: React.FC<PDFUploaderProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const toast = useToast();

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      if (!file.name.toLowerCase().endsWith(".pdf")) {
        toast({
          title: "Error",
          description: "Please upload a PDF file",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      setIsUploading(true);
      setUploadProgress(0);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch("http://localhost:8000/upload/", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Upload failed");
        }

        setUploadProgress(100);
        onUploadSuccess();
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to upload PDF",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      } finally {
        setIsUploading(false);
      }
    },
    [onUploadSuccess, toast]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    multiple: false,
  });

  return (
    <Box
      {...getRootProps()}
      p={10}
      border="2px dashed"
      borderColor={isDragActive ? "brand.500" : "gray.200"}
      borderRadius="md"
      textAlign="center"
      cursor="pointer"
      _hover={{ borderColor: "brand.500" }}
    >
      <input {...getInputProps()} />
      <VStack spacing={4}>
        <Text fontSize="lg">
          {isDragActive
            ? "Drop the PDF here"
            : "Drag and drop a PDF file here, or click to select"}
        </Text>
        <Button
          colorScheme="brand"
          isLoading={isUploading}
          loadingText="Uploading..."
        >
          Select PDF
        </Button>
        {isUploading && (
          <Progress
            value={uploadProgress}
            size="sm"
            width="100%"
            colorScheme="brand"
          />
        )}
      </VStack>
    </Box>
  );
};

export default PDFUploader;
