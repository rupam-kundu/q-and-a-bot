import Head from "next/head";
import { useState } from "react";

import FileQandAArea from "../components/FileQandAArea";
import { FileLite } from "../types/file";
import FileUploadArea from "../components/FileUploadArea";

export default function FileQandA() {
  const [files, setFiles] = useState<FileLite[]>([]);

  return (
    <div className="flex items-center text-left h-screen flex-col">
      <Head>
        <title>File Q&A Bot</title>
      </Head>
      <div className="max-w-xl w-full mx-auto m-8 space-y-8 text-gray-800">
        <h1 className="flex justify-center text-4xl">File Q&A Bot</h1>

        {/* 
        <div className="">
          To search for answers from the content in your files, upload them here
          and we will use OpenAI embeddings and GPT to find answers from the
          relevant documents.
        </div>

        <FileUploadArea
          handleSetFiles={setFiles}
          maxNumFiles={75}
          maxFileSizeMB={30}
        />
        */}

        <FileQandAArea files={files} />
      </div>
    </div>
  );
}
