import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import App from "./App";

describe("KeyQuest App", () => {
  it("renders Start Tutorial and adaptive copy", () => {
    render(<App />);
    expect(screen.getByRole("button", { name: /start tutorial/i })).toBeInTheDocument();
    expect(screen.getByText(/round timing adapts to your skill/i)).toBeInTheDocument();
  });
});
