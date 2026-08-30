# SRC-FRONTEND-001 - Checkout web frontend

Artifact type: source_code
Project: ecommerce-demo
Feature: FEATURE-CHECKOUT
Status: approved

## Content

React/TypeScript UI submits card or wallet checkout requests to /api/v1/checkout and always sends a demo user identity.

## Relationships

- implements: US-PAYMENT-001, US-WALLET-001

Source path: `sample-project/ecommerce/frontend/src/main.tsx`

## Connected source/test implementation

```
import React, {useState} from "react";
import {createRoot} from "react-dom/client";

function App() {
  const [result, setResult] = useState<string>("");
  async function checkout(method: "card" | "wallet") {
    const response = await fetch("/api/v1/checkout", {
      method: "POST",
      headers: {"Content-Type": "application/json", "x-user-id": "demo-user"},
      body: JSON.stringify({cart_id: "demo-cart", payment_method: method, amount: 42.50, idempotency_key: crypto.randomUUID()})
    });
    setResult(JSON.stringify(await response.json(), null, 2));
  }
  return <main style={{fontFamily:"sans-serif", maxWidth:800, margin:"40px auto"}}>
    <h1>SDLC-Guard Demo Commerce</h1>
    <p>This UI exists primarily so SDLC-Guard has realistic frontend source artifacts to trace.</p>
    <button onClick={() => checkout("card")}>Checkout with card</button>{" "}
    <button onClick={() => checkout("wallet")}>Checkout with wallet</button>
    <pre>{result}</pre>
  </main>;
}

createRoot(document.getElementById("root")!).render(<App/>);

```
