"""
LLM Prompt Fuzzer

Fuzzes LLM prompts to discover edge cases, crashes, unexpected behaviors,
and potential vulnerabilities.

Category: Testing/Fuzzing
"""

import httpx
import random
import string
import time
from typing import Optional, Dict, Any, List
from metaLLM.base.module import AuxiliaryModule
from metaLLM.base.option import Option, OptionType
from metaLLM.base.result import Result, ResultStatus
from metaLLM.base.target import LLMTarget


class PromptFuzzer(AuxiliaryModule):
    """
    Prompt Fuzzing Module

    Systematically tests LLM boundaries through fuzzing techniques:
        - Length-based fuzzing (very short, very long prompts)
        - Character set fuzzing (special chars, unicode, control chars)
        - Format fuzzing (malformed JSON, XML, code)
        - Semantic fuzzing (nonsensical prompts, contradictions)
        - Injection fuzzing (SQL, XSS, command injection attempts)
        - Resource exhaustion (token limits, computation)
    """

    def __init__(self):
        super().__init__()

        # Metadata
        self.name = "LLM Prompt Fuzzer"
        self.description = (
            "Fuzzes LLM prompts to discover edge cases, crashes, unexpected behaviors, "
            "and potential vulnerabilities through systematic input variation."
        )
        self.author = "Scott Thornton"

        # Options
        self.options = {
            "FUZZ_TYPE": Option(
                required=True,
                description="Type of fuzzing to perform",
                type=OptionType.ENUM,
                enum_values=["length", "charset", "format", "semantic", "injection", "comprehensive"],
                default="comprehensive"
            ),
            "NUM_TESTS": Option(
                required=False,
                description="Number of fuzz test cases to generate",
                type=OptionType.INTEGER,
                default=50
            ),
            "MAX_LENGTH": Option(
                required=False,
                description="Maximum prompt length for length fuzzing",
                type=OptionType.INTEGER,
                default=10000
            ),
            "DETECT_CRASHES": Option(
                required=False,
                description="Attempt to detect crashes or errors",
                type=OptionType.BOOLEAN,
                default=True
            ),
            "LOG_RESPONSES": Option(
                required=False,
                description="Log all responses for analysis",
                type=OptionType.BOOLEAN,
                default=True
            ),
            "DELAY_MS": Option(
                required=False,
                description="Delay between requests in milliseconds",
                type=OptionType.INTEGER,
                default=500
            ),
        }

        # Fuzz test results
        self.test_results = []

    def run(self) -> Result:
        """
        Execute prompt fuzzing

        Returns:
            Result object with fuzzing results
        """
        if not isinstance(self.target, LLMTarget):
            return Result(
                status=ResultStatus.ERROR,
                message="Target must be an LLMTarget",
                severity="info"
            )

        fuzz_type = self.options["FUZZ_TYPE"].value
        num_tests = self.options["NUM_TESTS"].value

        fuzz_results = {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "errors_detected": 0,
            "crashes_detected": 0,
            "anomalies": [],
            "interesting_cases": [],
        }

        # Generate and execute fuzz tests
        if fuzz_type == "comprehensive":
            # Run all fuzz types
            test_cases = []
            per_type = num_tests // 5

            test_cases.extend(self._generate_length_fuzzes(per_type))
            test_cases.extend(self._generate_charset_fuzzes(per_type))
            test_cases.extend(self._generate_format_fuzzes(per_type))
            test_cases.extend(self._generate_semantic_fuzzes(per_type))
            test_cases.extend(self._generate_injection_fuzzes(per_type))
        else:
            # Run specific fuzz type
            if fuzz_type == "length":
                test_cases = self._generate_length_fuzzes(num_tests)
            elif fuzz_type == "charset":
                test_cases = self._generate_charset_fuzzes(num_tests)
            elif fuzz_type == "format":
                test_cases = self._generate_format_fuzzes(num_tests)
            elif fuzz_type == "semantic":
                test_cases = self._generate_semantic_fuzzes(num_tests)
            elif fuzz_type == "injection":
                test_cases = self._generate_injection_fuzzes(num_tests)
            else:
                test_cases = []

        # Execute test cases
        for i, test_case in enumerate(test_cases):
            fuzz_results["total_tests"] += 1

            try:
                result = self._execute_fuzz_test(test_case)

                if result["success"]:
                    fuzz_results["successful_tests"] += 1
                else:
                    fuzz_results["failed_tests"] += 1

                if result.get("error"):
                    fuzz_results["errors_detected"] += 1

                if result.get("crash"):
                    fuzz_results["crashes_detected"] += 1
                    fuzz_results["interesting_cases"].append(result)

                if result.get("anomaly"):
                    fuzz_results["anomalies"].append(result)

                # Store result
                if self.options["LOG_RESPONSES"].value:
                    self.test_results.append(result)

                # Delay between requests
                if i < len(test_cases) - 1:
                    time.sleep(self.options["DELAY_MS"].value / 1000.0)

            except Exception as e:
                fuzz_results["failed_tests"] += 1
                fuzz_results["errors_detected"] += 1

        # Analyze results
        analysis = self._analyze_results(fuzz_results)

        # Determine severity based on findings
        if fuzz_results["crashes_detected"] > 0:
            severity = "high"
        elif fuzz_results["errors_detected"] > num_tests * 0.1:
            severity = "medium"
        else:
            severity = "low"

        return Result(
            status=ResultStatus.SUCCESS,
            message=f"Fuzzing complete. Executed {fuzz_results['total_tests']} tests.",
            severity=severity,
            data={
                **fuzz_results,
                "analysis": analysis,
            },
            evidence=[
                f"Total tests: {fuzz_results['total_tests']}",
                f"Successful: {fuzz_results['successful_tests']}",
                f"Errors: {fuzz_results['errors_detected']}",
                f"Crashes: {fuzz_results['crashes_detected']}",
                f"Anomalies: {len(fuzz_results['anomalies'])}",
            ]
        )

    def _generate_length_fuzzes(self, count: int) -> List[Dict[str, Any]]:
        """Generate length-based fuzz tests"""
        tests = []
        max_length = self.options["MAX_LENGTH"].value

        # Empty prompt
        tests.append({
            "type": "length",
            "subtype": "empty",
            "prompt": ""
        })

        # Single character
        tests.append({
            "type": "length",
            "subtype": "single_char",
            "prompt": "a"
        })

        # Very short (2-10 chars)
        for i in range(min(5, count // 5)):
            length = random.randint(2, 10)
            tests.append({
                "type": "length",
                "subtype": "very_short",
                "prompt": "a" * length
            })

        # Medium (100-1000 chars)
        for i in range(min(5, count // 5)):
            length = random.randint(100, 1000)
            tests.append({
                "type": "length",
                "subtype": "medium",
                "prompt": "test " * (length // 5)
            })

        # Long (1000-5000 chars)
        for i in range(min(5, count // 5)):
            length = random.randint(1000, 5000)
            tests.append({
                "type": "length",
                "subtype": "long",
                "prompt": "testing " * (length // 8)
            })

        # Very long (approaching max)
        for i in range(min(count - len(tests), 5)):
            length = random.randint(5000, max_length)
            tests.append({
                "type": "length",
                "subtype": "very_long",
                "prompt": "x" * length
            })

        return tests[:count]

    def _generate_charset_fuzzes(self, count: int) -> List[Dict[str, Any]]:
        """Generate character set fuzz tests"""
        tests = []

        # Special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        tests.append({
            "type": "charset",
            "subtype": "special_chars",
            "prompt": special_chars * 10
        })

        # Unicode characters
        tests.append({
            "type": "charset",
            "subtype": "unicode",
            "prompt": "Hello 世界 🌍 Здравствуй مرحبا"
        })

        # Control characters
        tests.append({
            "type": "charset",
            "subtype": "control_chars",
            "prompt": "test\x00\x01\x02\x03\x04"
        })

        # Newlines and whitespace
        tests.append({
            "type": "charset",
            "subtype": "whitespace",
            "prompt": "\n" * 100 + "\t" * 50 + " " * 200
        })

        # Mixed random
        for i in range(count - len(tests)):
            charset = string.ascii_letters + string.digits + string.punctuation
            prompt_len = random.randint(50, 500)
            tests.append({
                "type": "charset",
                "subtype": "random_mix",
                "prompt": ''.join(random.choices(charset, k=prompt_len))
            })

        return tests[:count]

    def _generate_format_fuzzes(self, count: int) -> List[Dict[str, Any]]:
        """Generate format-based fuzz tests"""
        tests = []

        # Malformed JSON
        tests.append({
            "type": "format",
            "subtype": "malformed_json",
            "prompt": '{"key": "value", "incomplete": '
        })

        # Malformed XML
        tests.append({
            "type": "format",
            "subtype": "malformed_xml",
            "prompt": '<root><tag>value</tag>'
        })

        # Malformed code
        tests.append({
            "type": "format",
            "subtype": "malformed_code",
            "prompt": "def function():\n  if True\n    return"
        })

        # Nested structures
        tests.append({
            "type": "format",
            "subtype": "deep_nesting",
            "prompt": "(" * 500 + "test" + ")" * 500
        })

        # Random format mixing
        for i in range(count - len(tests)):
            formats = [
                '{"json": true, "data": [1,2,3]}',
                '<xml><data>test</data></xml>',
                'function test() { return true; }',
                '# Markdown\n## Header\n- List item',
            ]
            tests.append({
                "type": "format",
                "subtype": "format_mix",
                "prompt": random.choice(formats)
            })

        return tests[:count]

    def _generate_semantic_fuzzes(self, count: int) -> List[Dict[str, Any]]:
        """Generate semantic fuzz tests"""
        tests = []

        # Nonsense
        tests.append({
            "type": "semantic",
            "subtype": "nonsense",
            "prompt": "blarg flimflam zibzab quirk snorf wobble"
        })

        # Contradictions
        tests.append({
            "type": "semantic",
            "subtype": "contradiction",
            "prompt": "Explain why 1+1=3 and simultaneously prove that 1+1=2"
        })

        # Recursive references
        tests.append({
            "type": "semantic",
            "subtype": "recursive",
            "prompt": "This sentence is false. The previous sentence is true."
        })

        # Category confusion
        tests.append({
            "type": "semantic",
            "subtype": "category_confusion",
            "prompt": "What is the color of jealousy's sound?"
        })

        # Random semantic tests
        nonsense_words = ["blarg", "flimflam", "zibzab", "quirk", "snorf", "wobble", "plonk", "squidge"]
        for i in range(count - len(tests)):
            prompt = " ".join(random.choices(nonsense_words, k=random.randint(5, 15)))
            tests.append({
                "type": "semantic",
                "subtype": "random_nonsense",
                "prompt": prompt
            })

        return tests[:count]

    def _generate_injection_fuzzes(self, count: int) -> List[Dict[str, Any]]:
        """Generate injection-based fuzz tests"""
        tests = []

        # SQL injection attempts
        tests.append({
            "type": "injection",
            "subtype": "sql",
            "prompt": "'; DROP TABLE users; --"
        })

        # XSS attempts
        tests.append({
            "type": "injection",
            "subtype": "xss",
            "prompt": "<script>alert('XSS')</script>"
        })

        # Command injection
        tests.append({
            "type": "injection",
            "subtype": "command",
            "prompt": "; rm -rf / ;"
        })

        # Path traversal
        tests.append({
            "type": "injection",
            "subtype": "path_traversal",
            "prompt": "../../../etc/passwd"
        })

        # Template injection
        tests.append({
            "type": "injection",
            "subtype": "template",
            "prompt": "{{7*7}} ${7*7} <%= 7*7 %>"
        })

        # Additional random injections
        injection_payloads = [
            "' OR '1'='1",
            "1' UNION SELECT * FROM users--",
            "<img src=x onerror=alert(1)>",
            "${IFS}cat${IFS}/etc/passwd",
            "{{config.items()}}",
        ]

        for i in range(count - len(tests)):
            tests.append({
                "type": "injection",
                "subtype": "random",
                "prompt": random.choice(injection_payloads)
            })

        return tests[:count]

    def _execute_fuzz_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single fuzz test"""
        result = {
            "test_case": test_case,
            "success": False,
            "response": None,
            "error": None,
            "crash": False,
            "anomaly": False,
            "response_time": 0.0,
        }

        try:
            start_time = time.time()
            response = self._send_prompt(test_case["prompt"])
            end_time = time.time()

            result["response_time"] = end_time - start_time

            if response:
                result["success"] = True
                result["response"] = response[:500]  # Truncate for storage

                # Check for anomalies
                if len(response) == 0:
                    result["anomaly"] = True
                    result["anomaly_type"] = "empty_response"

                if len(response) > 10000:
                    result["anomaly"] = True
                    result["anomaly_type"] = "excessively_long_response"

                if result["response_time"] > 30.0:
                    result["anomaly"] = True
                    result["anomaly_type"] = "slow_response"

            else:
                result["success"] = False
                result["error"] = "No response received"

        except httpx.TimeoutException:
            result["error"] = "Request timeout"
            result["crash"] = True
        except httpx.HTTPStatusError as e:
            result["error"] = f"HTTP {e.response.status_code}"
            if e.response.status_code >= 500:
                result["crash"] = True
        except Exception as e:
            result["error"] = str(e)
            result["crash"] = True

        return result

    def _send_prompt(self, prompt: str) -> Optional[str]:
        """Send prompt to LLM"""
        if not self.target:
            return None

        target = self.target
        assert isinstance(target, LLMTarget)

        headers = {}
        if target.api_key:
            headers["Authorization"] = f"Bearer {target.api_key}"

        payload = {"prompt": prompt}

        if target.model_name:
            payload["model"] = target.model_name

        with httpx.Client() as client:
            response = client.post(
                target.url,
                headers=headers,
                json=payload,
                timeout=30.0
            )

            response.raise_for_status()
            data = response.json()

            if "response" in data:
                return data["response"]
            elif "text" in data:
                return data["text"]
            elif "content" in data:
                return data["content"]

            return None

    def _analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fuzzing results"""
        analysis = {
            "error_rate": 0.0,
            "crash_rate": 0.0,
            "anomaly_rate": 0.0,
            "most_problematic_type": None,
            "recommendations": [],
        }

        total = results["total_tests"]

        if total > 0:
            analysis["error_rate"] = results["errors_detected"] / total
            analysis["crash_rate"] = results["crashes_detected"] / total
            analysis["anomaly_rate"] = len(results["anomalies"]) / total

        # Determine most problematic type
        type_errors = {}
        for test_result in self.test_results:
            if test_result.get("error") or test_result.get("crash"):
                test_type = test_result["test_case"]["type"]
                type_errors[test_type] = type_errors.get(test_type, 0) + 1

        if type_errors:
            analysis["most_problematic_type"] = max(type_errors, key=type_errors.get)

        # Generate recommendations
        if analysis["crash_rate"] > 0.05:
            analysis["recommendations"].append("High crash rate detected. Review input validation.")

        if analysis["error_rate"] > 0.1:
            analysis["recommendations"].append("High error rate. Consider implementing better error handling.")

        if analysis["anomaly_rate"] > 0.15:
            analysis["recommendations"].append("Many anomalous responses detected. Review response consistency.")

        return analysis
