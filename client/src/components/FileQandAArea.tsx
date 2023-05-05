import React, { memo, useCallback, useRef, useState } from "react";
import { Transition } from "@headlessui/react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

import FileViewerList from "./FileViewerList";
import LoadingText from "./LoadingText";
import { isFileNameInString } from "../services/utils";
import { FileChunk, FileLite } from "../types/file";
import { SERVER_ADDRESS } from "../types/constants";

type FileQandAAreaProps = {
  files: FileLite[];
};

function FileQandAArea(props: FileQandAAreaProps) {
  const searchBarRef = useRef(null);
  const [answerError, setAnswerError] = useState("");
  const [searchResultsLoading, setSearchResultsLoading] =
    useState<boolean>(false);
  const [answer, setAnswer] = useState("");

  const handleSearch = useCallback(async () => {
    if (searchResultsLoading) {
      return;
    }

    const question = (searchBarRef?.current as any)?.value ?? "";
    setAnswer("");

    if (!question) {
      setAnswerError("Please ask a question.");
      return;
    }
    /*
    if (props.files.length === 0) {
      setAnswerError("Please upload files before asking a question.");
      return;
    }
    */
    setSearchResultsLoading(true);
    setAnswerError("");

    let results: FileChunk[] = [];

    try {
      const answerResponse = await axios.post(
        `${SERVER_ADDRESS}/answer_question`,
        {
          question,
        }
      );
      console.log(answerResponse);
      if (answerResponse.status === 200) {
        console.log(answerResponse.data);
        setAnswer(answerResponse.data);
      } else {
        setAnswerError("Sorry, something went wrong!");
      }
    } catch (err: any) {
      setAnswerError("Sorry, something went wrong!");
    }

    setSearchResultsLoading(false);
    //  }, [props.files, searchResultsLoading]);
  }, [searchResultsLoading]);

  const handleEnterInSearchBar = useCallback(
    async (event: React.SyntheticEvent) => {
      if ((event as any).key === "Enter") {
        await handleSearch();
      }
    },
    [handleSearch]
  );

  return (
    <div className="space-y-4 text-gray-800">
      <div className="mt-2">
        Ask a question based on the content of the article titled{" "}
        <a
          className="text-blue-500 hover:underline"
          href="https://www.cell.com/cell/fulltext/S0092-8674(13)00645-4?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS0092867413006454%3Fshowall%3Dtrue"
          target="_blank"
          rel="noopener noreferrer"
        >
          The Hallmarks of Aging
        </a>
        {"."}
      </div>
      <div className="space-y-2">
        <input
          className="border rounded border-gray-200 w-full mb-2 py-1 px-2"
          placeholder="e.g. What is aging?"
          name="search"
          ref={searchBarRef}
          onKeyDown={handleEnterInSearchBar}
        />
        <div className="flex justify-center">
          <div
            className="rounded-md bg-gray-50 mt-2 py-1 px-4 w-max text-gray-500 hover:bg-gray-100 border border-gray-100 shadow cursor-pointer"
            onClick={handleSearch}
          >
            {searchResultsLoading ? (
              <LoadingText text="Answering question..." />
            ) : (
              "Ask question"
            )}
          </div>
        </div>
      </div>
      <div className="">
        {answerError && <div className="text-red-500">{answerError}</div>}
        <Transition
          show={answer !== ""}
          enter="transition duration-600 ease-out"
          enterFrom="transform opacity-0"
          enterTo="transform opacity-100"
          leave="transition duration-125 ease-out"
          leaveFrom="transform opacity-100"
          leaveTo="transform opacity-0"
          className="mb-8"
        >
          {/* answer from files */}
          {answer && (
            <div className="">
              <ReactMarkdown className="prose" linkTarget="_blank">
                {answer}
              </ReactMarkdown>
            </div>
          )}

          <Transition
            show={
              props.files.filter((file) =>
                isFileNameInString(file.name, answer)
              ).length > 0
            }
            enter="transition duration-600 ease-out"
            enterFrom="transform opacity-0"
            enterTo="transform opacity-100"
            leave="transition duration-125 ease-out"
            leaveFrom="transform opacity-100"
            leaveTo="transform opacity-0"
            className="mb-8"
          >
            <FileViewerList
              files={props.files.filter((file) =>
                isFileNameInString(file.name, answer)
              )}
              title="Sources"
              listExpanded={true}
            />
          </Transition>
        </Transition>
      </div>
    </div>
  );
}

export default memo(FileQandAArea);
