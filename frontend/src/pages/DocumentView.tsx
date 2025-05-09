import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  Input,
  Button,
  useToast,
  Spinner,
  HStack,
  Flex,
  Avatar,
  InputGroup,
  InputRightElement,
  Tag,
  Wrap,
  WrapItem,
  IconButton,
} from "@chakra-ui/react";
import { keyframes } from "@emotion/react";
import { ArrowForwardIcon, ArrowBackIcon } from "@chakra-ui/icons";
import { Document, Question, Answer } from "../types";

// Message types for the chat
interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
}

// Define loading animation keyframes
const typingAnimation = keyframes`
  0% { transform: translateY(0px); }
  28% { transform: translateY(-5px); }
  44% { transform: translateY(0px); }
`;

// Define new pulse animation keyframes
const pulseAnimation = keyframes`
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
`;

// Define shimmer animation for loading cards
const shimmerAnimation = keyframes`
  0% { background-position: -468px 0; }
  100% { background-position: 468px 0; }
`;

// Typing indicator component
const TypingIndicator = () => {
  const animationDelay = (i: number) => `${i * 0.15}s`;

  return (
    <HStack spacing={1} p={1}>
      {[0, 1, 2].map((i) => (
        <Box
          key={i}
          h="8px"
          w="8px"
          bg="brand.500"
          borderRadius="full"
          animation={`${typingAnimation} 1.5s infinite`}
          sx={{ animationDelay: animationDelay(i) }}
        />
      ))}
    </HStack>
  );
};

// Component for suggestion loading animation
const SuggestionLoadingAnimation = () => {
  return (
    <Wrap spacing={3}>
      {[1, 2, 3, 4].map((i) => (
        <WrapItem key={i}>
          <Box
            height="36px"
            width={`${80 + i * 40}px`}
            borderRadius="full"
            bg="gray.100"
            position="relative"
            overflow="hidden"
            _after={{
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              background:
                "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.5) 50%, rgba(255,255,255,0) 100%)",
              animation: `${shimmerAnimation} 1.5s infinite linear`,
              backgroundSize: "600px 100%",
            }}
          />
        </WrapItem>
      ))}
    </Wrap>
  );
};

const DocumentView = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [document, setDocument] = useState<Document | null>(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await fetch(`http://localhost:8000/documents/${id}`);
        if (!response.ok) {
          throw new Error("Document not found");
        }
        const data = await response.json();
        setDocument(data);

        // Add welcome message
        setMessages([
          {
            id: "welcome",
            text: `Hi there! I can answer questions about ${data.original_filename}. What would you like to know?`,
            sender: "ai",
            timestamp: new Date(),
          },
        ]);

        // Fetch suggested questions
        fetchSuggestedQuestions();
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to fetch document",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      }
    };

    fetchDocument();
  }, [id, toast]);

  const fetchSuggestedQuestions = async () => {
    if (!id) return;

    setLoadingSuggestions(true);
    try {
      const response = await fetch(
        `http://localhost:8000/documents/${id}/suggested-questions`
      );
      if (!response.ok) {
        throw new Error("Failed to fetch suggested questions");
      }
      const data = await response.json();
      setSuggestedQuestions(data.questions || []);
    } catch (error) {
      console.error("Error fetching suggested questions:", error);
      // We don't show a toast here to avoid cluttering the UI
    } finally {
      setLoadingSuggestions(false);
    }
  };

  useEffect(() => {
    // Scroll to bottom whenever messages change
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!question.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: question,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Clear input
    setQuestion("");

    // Show loading
    setIsLoading(true);

    try {
      const questionData: Question = {
        document_id: parseInt(id!),
        question: userMessage.text,
      };

      const response = await fetch("http://localhost:8000/ask/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(questionData),
      });

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      const data: Answer = await response.json();

      // Add AI response
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        text: data.answer,
        sender: "ai",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get answer",
        status: "error",
        duration: 3000,
        isClosable: true,
      });

      // Add error message
      const errorMessage: Message = {
        id: `ai-error-${Date.now()}`,
        text: "Sorry, I couldn't process your question. Please try again.",
        sender: "ai",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestionClick = (questionText: string) => {
    // Set question and then call handleSendMessage in a callback to ensure state is updated
    setQuestion(questionText);

    // Need to manually create and send the message since we can't wait for state update
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: questionText,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Show loading
    setIsLoading(true);

    // Make the API call
    const questionData: Question = {
      document_id: parseInt(id!),
      question: questionText,
    };

    fetch("http://localhost:8000/ask/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(questionData),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to get answer");
        }
        return response.json();
      })
      .then((data: Answer) => {
        // Add AI response
        const aiMessage: Message = {
          id: `ai-${Date.now()}`,
          text: data.answer,
          sender: "ai",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);
      })
      .catch((error) => {
        toast({
          title: "Error",
          description: "Failed to get answer",
          status: "error",
          duration: 3000,
          isClosable: true,
        });

        // Add error message
        const errorMessage: Message = {
          id: `ai-error-${Date.now()}`,
          text: "Sorry, I couldn't process your question. Please try again.",
          sender: "ai",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!document) {
    return (
      <Container centerContent py={8}>
        <Spinner size="xl" />
      </Container>
    );
  }

  return (
    <Container
      maxW="container.xl"
      py={4}
      h="90vh"
      display="flex"
      flexDirection="column"
    >
      {/* Header */}
      <Flex justifyContent="space-between" alignItems="center" mb={4}>
        <Flex alignItems="center">
          <IconButton
            aria-label="Back to documents"
            icon={<ArrowBackIcon />}
            variant="ghost"
            mr={2}
            onClick={() => navigate("/")}
            size="md"
          />
          <Box>
            <Heading size="md">{document.original_filename}</Heading>
            <Text fontSize="sm" color="gray.500">
              Uploaded on {new Date(document.upload_date).toLocaleDateString()}
            </Text>
          </Box>
        </Flex>
      </Flex>

      {/* Chat Container */}
      <Box
        flex="1"
        overflowY="auto"
        bg="gray.50"
        p={4}
        borderRadius="md"
        mb={4}
        shadow="sm"
      >
        <VStack spacing={4} align="stretch">
          {messages.map((message) => (
            <Flex
              key={message.id}
              justify={message.sender === "user" ? "flex-end" : "flex-start"}
            >
              {message.sender === "ai" && (
                <Avatar size="sm" name="AI Assistant" bg="brand.500" mr={2} />
              )}
              <Box
                maxW="70%"
                bg={message.sender === "user" ? "brand.500" : "white"}
                color={message.sender === "user" ? "white" : "black"}
                p={3}
                borderRadius="lg"
                shadow="md"
              >
                <Text>{message.text}</Text>
                <Text
                  fontSize="xs"
                  color={
                    message.sender === "user" ? "whiteAlpha.700" : "gray.500"
                  }
                  textAlign="right"
                  mt={1}
                >
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </Text>
              </Box>
              {message.sender === "user" && (
                <Avatar size="sm" name="User" bg="gray.500" ml={2} />
              )}
            </Flex>
          ))}
          <div ref={chatEndRef} />
          {isLoading && (
            <Flex justify="flex-start">
              <Avatar size="sm" name="AI Assistant" bg="brand.500" mr={2} />
              <Box
                bg="white"
                p={3}
                borderRadius="lg"
                shadow="md"
                minH="45px"
                display="flex"
                alignItems="center"
              >
                <TypingIndicator />
              </Box>
            </Flex>
          )}
        </VStack>
      </Box>

      {/* Suggested Questions */}
      {suggestedQuestions.length > 0 && (
        <Box
          mb={4}
          bg="white"
          borderRadius="lg"
          p={4}
          shadow="sm"
          borderTop="1px"
          borderColor="gray.100"
        >
          <Flex mb={3} alignItems="center">
            <Box
              bg="blue.500"
              color="white"
              borderRadius="md"
              px={2}
              py={1}
              mr={2}
            >
              <Text fontSize="xs" fontWeight="bold">
                SUGGESTIONS
              </Text>
            </Box>
            <Text fontSize="sm" color="gray.600" fontWeight="medium">
              Questions you might want to ask about this document:
            </Text>
          </Flex>

          <Wrap spacing={3} mt={2}>
            {suggestedQuestions.map((q, index) => (
              <WrapItem key={index}>
                <Tag
                  size="md"
                  variant="outline"
                  colorScheme="blue"
                  cursor="pointer"
                  py={2}
                  px={3}
                  borderRadius="full"
                  boxShadow="sm"
                  _hover={{
                    bg: "blue.50",
                    transform: "translateY(-2px)",
                    boxShadow: "md",
                  }}
                  transition="all 0.2s"
                  onClick={() => handleSuggestedQuestionClick(q)}
                >
                  <Text fontSize="sm">{q}</Text>
                </Tag>
              </WrapItem>
            ))}
          </Wrap>
        </Box>
      )}

      {/* Loading state for suggestions */}
      {loadingSuggestions && (
        <Box
          mb={4}
          p={4}
          bg="white"
          borderRadius="lg"
          shadow="sm"
          borderTop="1px"
          borderColor="gray.100"
        >
          <Flex mb={3} alignItems="center">
            <Box
              bg="blue.500"
              color="white"
              borderRadius="md"
              px={2}
              py={1}
              mr={2}
              animation={`${pulseAnimation} 2s infinite ease-in-out`}
            >
              <Text fontSize="xs" fontWeight="bold">
                GENERATING
              </Text>
            </Box>
            <Text fontSize="sm" color="gray.600" fontWeight="medium">
              Creating questions based on document content...
            </Text>
          </Flex>

          <Box mt={3}>
            <SuggestionLoadingAnimation />
          </Box>
        </Box>
      )}

      {/* Input Area */}
      <Box
        p={4}
        bg="white"
        borderRadius="lg"
        shadow="md"
        borderTop="1px"
        borderColor="gray.100"
      >
        <InputGroup size="md">
          <Input
            placeholder="Ask a question about the document..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            borderRadius="full"
            bg="gray.50"
            py={6}
            fontWeight="medium"
            _focus={{
              boxShadow: "0 0 0 1px #3182ce",
              borderColor: "blue.500",
              bg: "white",
            }}
            _hover={{ bg: "white" }}
          />
          <InputRightElement width="4.5rem" h="full" pr={1}>
            <Button
              borderRadius="full"
              colorScheme="blue"
              onClick={handleSendMessage}
              isLoading={isLoading}
              size="sm"
              px={6}
            >
              <ArrowForwardIcon />
            </Button>
          </InputRightElement>
        </InputGroup>
      </Box>
    </Container>
  );
};

export default DocumentView;
