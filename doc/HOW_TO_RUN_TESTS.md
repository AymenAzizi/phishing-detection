# 🧪 How to Run the Comprehensive Test Suite

This guide explains how to run all the tests for the Phishing Detection Platform.

---

## 📋 Prerequisites

Before running tests, ensure:
1. ✅ Both servers are running:
   - Backend API on port 8000
   - Dashboard on port 3000
2. ✅ Python 3.7+ is installed
3. ✅ Required packages are installed: `requests`

### Start the Servers

**Terminal 1 - Backend API:**
```bash
python -m uvicorn real_api:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Dashboard:**
```bash
python -m uvicorn dashboard_server:dashboard_app --host 0.0.0.0 --port 3000
```

---

## 🚀 Running the Tests

### Option 1: Run All Tests (Recommended)

Run all three test suites in sequence:

```bash
# Run all tests
python TEST_ALL_FUNCTIONALITY.py
python TEST_EXTENSION_INTEGRATION.py
python TEST_DATA_AND_ERRORS.py
```

**Expected Output:**
- Each test suite will display results in real-time
- Final summary showing pass/fail status
- Total execution time: ~5 minutes

### Option 2: Run Individual Test Suites

#### Test Suite 1: Core Functionality (6 tests)
```bash
python TEST_ALL_FUNCTIONALITY.py
```

**Tests:**
- Backend API Health Check
- URL Prediction Endpoint
- Email Prediction Endpoint
- Dashboard Server Endpoints
- Real-Time Monitoring System
- Model Information

**Expected Result:** ✅ 6/6 PASSED

---

#### Test Suite 2: Extension & Integration (8 tests)
```bash
python TEST_EXTENSION_INTEGRATION.py
```

**Tests:**
- Extension Event Submission
- Phishing Event Submission
- Get Extension Events
- Clear History
- Monitoring Start/Stop
- Monitoring Events
- Monitoring Summary
- Dashboard Loading

**Expected Result:** ✅ 8/8 PASSED

---

#### Test Suite 3: Data Persistence & Error Handling (10 tests)
```bash
python TEST_DATA_AND_ERRORS.py
```

**Tests:**
- Model File Persistence
- Database File Persistence
- Feature Extractor File
- Invalid URL Handling
- Invalid Email Handling
- API Timeout Handling
- CORS Headers
- Response Format Validation
- Concurrent Request Handling
- Large URL Handling

**Expected Result:** ✅ 10/10 PASSED

---

## 📊 Understanding Test Output

### Color Coding
- 🟢 **Green (✅ PASS)** - Test passed successfully
- 🔴 **Red (❌ FAIL)** - Test failed
- 🟡 **Yellow** - Section headers and information
- 🔵 **Blue** - Test suite headers

### Example Output
```
======================================================================
                   TEST 1: BACKEND API HEALTH CHECK                   
======================================================================

  ✅ PASS | API Health Check
       └─ Status: healthy
  ✅ PASS | Model Loaded
       └─ Model: True
  ✅ PASS | Feature Extractor
       └─ Ready: True
```

### Summary Section
```
======================================================================
                             TEST SUMMARY
======================================================================

  ✅ PASS | API Health
  ✅ PASS | URL Predictions
  ✅ PASS | Email Predictions
  ✅ PASS | Dashboard Endpoints
  ✅ PASS | Monitoring System
  ✅ PASS | Model Info

Overall: 6/6 tests passed (100%)

🎉 ALL TESTS PASSED! 🎉
```

---

## 🔍 Interpreting Results

### All Tests Pass (100%)
```
Overall: 24/24 tests passed (100%)
🎉 ALL TESTS PASSED! 🎉
```
✅ **Status:** System is fully operational and ready for production

### Some Tests Fail
```
Overall: 20/24 tests passed (83%)
⚠️ SOME TESTS FAILED
```
⚠️ **Status:** Review failed tests and check server logs

---

## 🐛 Troubleshooting

### Issue: "Connection refused" errors

**Solution:**
1. Verify both servers are running
2. Check ports 8000 and 3000 are not in use
3. Restart servers:
   ```bash
   # Kill existing processes
   taskkill /F /IM python.exe
   
   # Restart servers
   python -m uvicorn real_api:app --host 0.0.0.0 --port 8000
   python -m uvicorn dashboard_server:dashboard_app --host 0.0.0.0 --port 3000
   ```

### Issue: "Module not found" errors

**Solution:**
1. Install required packages:
   ```bash
   pip install requests
   ```
2. Ensure you're in the correct directory:
   ```bash
   cd "Downloads/Projet tekup/phishing dectection aymen"
   ```

### Issue: Tests timeout

**Solution:**
1. Check if servers are responding:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000/api/system-status
   ```
2. Increase timeout in test scripts if needed
3. Check system resources (CPU, memory)

---

## 📈 Performance Benchmarks

Expected performance metrics:

| Metric | Expected | Actual |
|--------|----------|--------|
| URL Prediction | <100ms | ~100ms |
| Email Prediction | <50ms | ~50ms |
| Dashboard Response | <50ms | <50ms |
| Safe URL Accuracy | 100% | 100% |
| Phishing Detection | 100% | 100% |

---

## 📝 Test Reports

After running tests, review the generated reports:

### 1. COMPREHENSIVE_TEST_REPORT.md
- Detailed test results
- Performance metrics
- Deployment readiness assessment
- Key findings and recommendations

### 2. FULL_TEST_SUMMARY.txt
- Quick reference summary
- All test results in table format
- Key findings
- Deployment status

---

## 🔄 Continuous Testing

### Run Tests Regularly
```bash
# Create a batch file for easy testing
# save as: run_all_tests.bat

@echo off
echo Starting comprehensive tests...
python TEST_ALL_FUNCTIONALITY.py
python TEST_EXTENSION_INTEGRATION.py
python TEST_DATA_AND_ERRORS.py
echo All tests completed!
pause
```

### Automated Testing (Optional)
```bash
# Run tests every hour
# Windows Task Scheduler or cron job
```

---

## ✅ Verification Checklist

Before considering tests complete:

- [ ] All 24 tests passed
- [ ] No error messages in output
- [ ] Response times are acceptable
- [ ] Accuracy metrics are 100%
- [ ] Test reports generated
- [ ] No warnings or issues

---

## 📞 Support

If tests fail:
1. Check server logs for errors
2. Verify all dependencies are installed
3. Ensure ports 8000 and 3000 are available
4. Review the DIAGNOSTIC_GUIDE.md for troubleshooting

---

## 🎯 Next Steps

After successful testing:
1. ✅ Review test reports
2. ✅ Verify all functionality works
3. ✅ Deploy to production (if approved)
4. ✅ Monitor performance in production
5. ✅ Collect user feedback

---

**Happy Testing! 🚀**

