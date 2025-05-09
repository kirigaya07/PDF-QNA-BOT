import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ChakraProvider, CSSReset } from "@chakra-ui/react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import DocumentView from "./pages/DocumentView";
import theme from "./theme";

function App() {
  return (
    <ChakraProvider theme={theme}>
      <CSSReset />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/document/:id" element={<DocumentView />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
